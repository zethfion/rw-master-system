#!/usr/bin/env python3
"""Audit a sanitized expert package before an explicitly approved release."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path


PRIVATE_DIRS = {"corpus", "consultations", "distillates"}
HIDDEN_CHARS = {"\u200b", "\u200c", "\u200d", "\u202a", "\u202b", "\u202d", "\u202e", "\u2066", "\u2067", "\u2068", "\u2069", "\ufeff"}
EMAIL = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
SECRETS = {
    "private key": re.compile(r"BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "API key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "authorization header": re.compile(r"Authorization:\s*Bearer\s+\S{16,}", re.IGNORECASE),
}
TEXT_SUFFIXES = {"", ".md", ".txt", ".json", ".csv", ".yaml", ".yml", ".toml"}


def audit_package(package: Path, manifest: dict[str, object] | None = None) -> list[str]:
    findings: list[str] = []
    if manifest is None:
        try:
            loaded = json.loads((package / ".master-system.json").read_text(encoding="utf-8"))
            manifest = loaded if isinstance(loaded, dict) else {}
        except (OSError, UnicodeError, json.JSONDecodeError):
            manifest = {}
    if manifest.get("public_release_allowed") is not True:
        findings.append("release requires explicit public_release_allowed true")

    for private_dir in PRIVATE_DIRS:
        root = package / private_dir
        if root.is_dir():
            exposed = [path for path in root.rglob("*") if path.is_file() and not path.name.startswith(".")]
            if exposed:
                findings.append(f"private directory contains releasable content: {private_dir}")

    for current, dirs, files in os.walk(package, followlinks=False):
        current_path = Path(current)
        for name in dirs:
            path = current_path / name
            if path.is_symlink():
                findings.append(f"symlink directory requires manual review: {path.relative_to(package)}")
        for name in files:
            path = current_path / name
            relative = path.relative_to(package)
            lower = name.lower()
            if path.is_symlink():
                findings.append(f"symlink requires manual review: {relative}")
                continue
            if lower == ".env" or lower.startswith(".env.") or lower.endswith((".key", ".pem", ".p12", ".pfx")):
                findings.append(f"sensitive filename: {relative}")
            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                continue
            for label, pattern in SECRETS.items():
                if pattern.search(text):
                    findings.append(f"{label}: {relative}")
            if EMAIL.search(text):
                findings.append(f"email address requires removal or explicit review: {relative}")
            if any(char in text for char in HIDDEN_CHARS):
                findings.append(f"hidden Unicode control: {relative}")
    return sorted(set(findings))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    package = args.package.expanduser().resolve()
    if not package.is_dir():
        print(f"ERROR: not a directory: {package}", file=sys.stderr)
        return 2
    findings = audit_package(package)
    if findings:
        for finding in findings:
            print(f"ERROR: {finding}", file=sys.stderr)
        return 1
    print(f"package release audit passed: {package}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
