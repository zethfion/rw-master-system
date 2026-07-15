#!/usr/bin/env python3
"""Validate an expert knowledge package at structure, MVP, or release level."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

from audit_master_package import audit_package


SCHEMA = "rw-master-system/v1"
REQUIRED_FILES = (
    ".master-system.json",
    "README.md",
    "soul.md",
    "index.md",
    "log.md",
    "evidence/sources.csv",
    "evidence/claims.csv",
    "evidence/open-questions.md",
)
REQUIRED_DIRS = (
    "corpus",
    "distillates",
    "frameworks",
    "examples",
    "evidence",
    "consultations",
)
SOURCE_COLUMNS = (
    "source_id",
    "title",
    "source_type",
    "url",
    "author",
    "speakers",
    "published_date",
    "access_basis",
    "evidence_level",
    "disposition",
    "local_path",
    "notes",
)
CLAIM_COLUMNS = ("claim_id", "claim", "status", "source_id", "anchor", "framework_id", "notes")
EVIDENCE_LEVELS = {"primary", "affiliated", "secondary", "inferred", "unknown"}
DISPOSITIONS = {"accepted", "excluded", "duplicate", "blocked", "pending"}
PLACEHOLDER = re.compile(r"\b(?:not yet|todo|tbd|placeholder)\b", re.IGNORECASE)


def read_csv(path: Path, expected: tuple[str, ...], errors: list[str]) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            columns = tuple(reader.fieldnames or ())
            if columns != expected:
                errors.append(f"{path.name} columns do not match the v1 schema")
                return []
            rows: list[dict[str, str]] = []
            for line_number, row in enumerate(reader, start=2):
                if None in row:
                    errors.append(f"{path.name} row {line_number} has too many columns")
                    continue
                rows.append({key: (value or "").strip() for key, value in row.items()})
            return rows
    except (OSError, UnicodeError, csv.Error) as exc:
        errors.append(f"invalid {path.name}: {exc}")
        return []


def read_manifest(path: Path, errors: list[str]) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"invalid manifest: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append("manifest must be a JSON object")
        return {}
    return value


def substantive(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError):
        return False
    meaningful = [line for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    return bool(meaningful) and not PLACEHOLDER.search("\n".join(meaningful))


def content_files(directory: Path, suffix: str | None = None) -> list[Path]:
    if not directory.is_dir():
        return []
    return [
        path
        for path in directory.rglob("*")
        if path.is_file()
        and not path.name.startswith(".")
        and (suffix is None or path.suffix.lower() == suffix)
    ]


def resolve_local_path(package: Path, value: str) -> Path | None:
    candidate = Path(value)
    if not value or candidate.is_absolute():
        return None
    resolved = (package / candidate).resolve()
    try:
        resolved.relative_to(package)
    except ValueError:
        return None
    return resolved


def validate_structure(package: Path, errors: list[str]) -> tuple[dict[str, object], list[dict[str, str]], list[dict[str, str]]]:
    manifest: dict[str, object] = {}
    source_rows: list[dict[str, str]] = []
    claim_rows: list[dict[str, str]] = []
    if not package.is_dir():
        errors.append(f"not a directory: {package}")
        return manifest, source_rows, claim_rows

    for relative in REQUIRED_FILES:
        if not (package / relative).is_file():
            errors.append(f"missing file: {relative}")
    for relative in REQUIRED_DIRS:
        if not (package / relative).is_dir():
            errors.append(f"missing directory: {relative}")

    manifest_path = package / ".master-system.json"
    if manifest_path.is_file():
        manifest = read_manifest(manifest_path, errors)
        if manifest.get("schema") != SCHEMA:
            errors.append(f"unexpected schema: {manifest.get('schema')!r}")
        generator = manifest.get("generator")
        if not isinstance(generator, dict):
            errors.append("manifest generator must be an object")
        else:
            if generator.get("name") != "rw-master-system-builder":
                errors.append("unexpected generator name")
            if generator.get("network_telemetry") is not False:
                errors.append("manifest must declare network_telemetry false")
            version_path = Path(__file__).resolve().parent.parent / "VERSION"
            try:
                expected_version = version_path.read_text(encoding="utf-8").strip()
            except OSError as exc:
                errors.append(f"cannot read bundled VERSION: {exc}")
            else:
                if generator.get("version") != expected_version:
                    errors.append("manifest generator version does not match bundled VERSION")
        if manifest.get("content_scope") != "private-user-controlled":
            errors.append("manifest content_scope must be private-user-controlled")
        if not isinstance(manifest.get("public_release_allowed"), bool):
            errors.append("manifest public_release_allowed must be boolean")

    sources = package / "evidence" / "sources.csv"
    if sources.is_file():
        source_rows = read_csv(sources, SOURCE_COLUMNS, errors)
    claims = package / "evidence" / "claims.csv"
    if claims.is_file():
        claim_rows = read_csv(claims, CLAIM_COLUMNS, errors)
    return manifest, source_rows, claim_rows


def validate_mvp(
    package: Path,
    source_rows: list[dict[str, str]],
    claim_rows: list[dict[str, str]],
    errors: list[str],
) -> None:
    accepted: dict[str, dict[str, str]] = {}
    seen_source_ids: set[str] = set()
    for index, row in enumerate(source_rows, start=2):
        source_id = row["source_id"]
        if not source_id:
            errors.append(f"sources.csv row {index} has no source_id")
            continue
        if source_id in seen_source_ids:
            errors.append(f"sources.csv has duplicate source_id: {source_id}")
        seen_source_ids.add(source_id)
        if row["evidence_level"] not in EVIDENCE_LEVELS:
            errors.append(f"sources.csv row {index} has invalid evidence_level")
        if row["disposition"] not in DISPOSITIONS:
            errors.append(f"sources.csv row {index} has invalid disposition")
        if row["disposition"] == "accepted":
            for field in ("title", "source_type", "access_basis", "evidence_level", "local_path"):
                if not row[field]:
                    errors.append(f"accepted source {source_id} is missing {field}")
            local_path = resolve_local_path(package, row["local_path"])
            if local_path is None or not local_path.is_file():
                errors.append(f"accepted source {source_id} has an unsafe or missing local_path")
            accepted[source_id] = row
    if not accepted:
        errors.append("MVP requires at least one accepted source")

    if not claim_rows:
        errors.append("MVP requires at least one evidence claim")
    seen_claim_ids: set[str] = set()
    for index, row in enumerate(claim_rows, start=2):
        claim_id = row["claim_id"]
        if not claim_id or claim_id in seen_claim_ids:
            errors.append(f"claims.csv row {index} has a missing or duplicate claim_id")
        seen_claim_ids.add(claim_id)
        for field in ("claim", "status", "source_id", "anchor"):
            if not row[field]:
                errors.append(f"claim {claim_id or index} is missing {field}")
        if row["source_id"] not in accepted:
            errors.append(f"claim {claim_id or index} does not reference an accepted source")

    frameworks = content_files(package / "frameworks", ".md")
    if len(frameworks) < 3:
        errors.append("MVP requires at least three framework cards")
    for framework in frameworks:
        try:
            text = framework.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            errors.append(f"cannot read framework: {framework.name}")
            continue
        if not substantive(framework):
            errors.append(f"framework is still a placeholder: {framework.name}")
        if not re.search(r"(?ms)^sources:\s*\n(?:\s+-\s+\S+\s*\n?)+", text):
            errors.append(f"framework has no source anchors: {framework.name}")

    for relative in ("soul.md", "index.md", "evidence/open-questions.md"):
        path = package / relative
        if path.is_file() and not substantive(path):
            errors.append(f"MVP content is still empty or placeholder: {relative}")
    examples = content_files(package / "examples")
    if not examples or not any(substantive(path) for path in examples):
        errors.append("MVP requires a substantive examples artifact")
    consultations = content_files(package / "consultations")
    consultation_examples = [path for path in examples if "consult" in path.name.lower()]
    if not any(substantive(path) for path in consultations + consultation_examples):
        errors.append("MVP requires a substantive consultation artifact")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("--level", choices=("structure", "mvp", "release"), default="structure")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    package = args.package.expanduser().resolve()
    errors: list[str] = []
    manifest, source_rows, claim_rows = validate_structure(package, errors)
    if args.level in {"mvp", "release"} and package.is_dir():
        validate_mvp(package, source_rows, claim_rows, errors)
    if args.level == "release" and package.is_dir():
        errors.extend(audit_package(package, manifest))

    result = {"valid": not errors, "level": args.level, "errors": errors}
    if args.as_json:
        print(json.dumps(result, indent=2))
        return 1 if errors else 0
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"valid ({args.level}): {package}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
