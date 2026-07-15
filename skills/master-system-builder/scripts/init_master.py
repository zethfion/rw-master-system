#!/usr/bin/env python3
"""Create a private expert knowledge package from bundled templates."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from datetime import date
from pathlib import Path


SCHEMA = "rw-master-system/v1"
CATEGORIES = (
    "emails",
    "books",
    "articles",
    "podcasts",
    "youtube",
    "courses",
    "webinars",
    "other",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="Parent knowledge directory")
    parser.add_argument("--id", required=True, help="Lowercase hyphenated expert ID")
    parser.add_argument("--display-name", required=True, help="Human-readable expert name")
    return parser.parse_args()


def validate_id(value: str) -> None:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        raise ValueError("--id must use lowercase letters, digits, and single hyphens")


def write_new(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(content)


def skill_version() -> str:
    """Read the canonical distribution version bundled with the skill."""
    version_path = Path(__file__).resolve().parent.parent / "VERSION"
    version = version_path.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError(f"invalid skill version in {version_path.name}")
    return version


def main() -> int:
    args = parse_args()
    temporary: Path | None = None
    try:
        validate_id(args.id)
        if not args.display_name.strip():
            raise ValueError("--display-name must not be empty")
        root = args.root.expanduser().resolve()
        root.mkdir(parents=True, exist_ok=True)
        package = root / args.id
        if package.exists():
            raise FileExistsError(f"refusing to overwrite existing package: {package}")
        temporary = Path(tempfile.mkdtemp(prefix=f".{args.id}.tmp-", dir=root))

        assets = Path(__file__).resolve().parent.parent / "assets"
        readme = (assets / "master-readme.md").read_text(encoding="utf-8")
        readme = readme.replace("{{DISPLAY_NAME}}", args.display_name)
        soul = (assets / "soul.md").read_text(encoding="utf-8")
        gitignore = (assets / "package.gitignore").read_text(encoding="utf-8")
        privacy = (assets / "privacy.md").read_text(encoding="utf-8")

        manifest = {
            "schema": SCHEMA,
            "generator": {
                "name": "rw-master-system-builder",
                "version": skill_version(),
                "network_telemetry": False,
            },
            "expert": {"id": args.id, "display_name": args.display_name},
            "created": date.today().isoformat(),
            "content_scope": "private-user-controlled",
            "public_release_allowed": False,
        }
        write_new(temporary / ".master-system.json", json.dumps(manifest, indent=2) + "\n")
        write_new(temporary / ".gitignore", gitignore)
        write_new(temporary / "README.md", readme)
        write_new(temporary / "PRIVACY.md", privacy)
        write_new(temporary / "soul.md", soul)
        write_new(temporary / "index.md", "# Index\n\nNot yet built.\n")
        write_new(temporary / "log.md", f"# Change log\n\n- {date.today().isoformat()}: package initialized.\n")

        for category in CATEGORIES:
            write_new(temporary / "corpus" / category / ".gitkeep", "")
        for directory in ("distillates", "frameworks", "examples", "consultations"):
            write_new(temporary / directory / ".gitkeep", "")

        write_new(
            temporary / "evidence" / "sources.csv",
            "source_id,title,source_type,url,author,speakers,published_date,access_basis,evidence_level,disposition,local_path,notes\n",
        )
        write_new(
            temporary / "evidence" / "claims.csv",
            "claim_id,claim,status,source_id,anchor,framework_id,notes\n",
        )
        write_new(temporary / "evidence" / "open-questions.md", "# Open questions\n")
        temporary.rename(package)
        temporary = None
    except (OSError, ValueError) as exc:
        if temporary is not None:
            shutil.rmtree(temporary, ignore_errors=True)
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(package)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
