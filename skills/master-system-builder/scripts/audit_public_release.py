#!/usr/bin/env python3
"""Fail a public-release audit on common secrets, private paths, or hidden text."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules"}
TEXT_EXTENSIONS = {"", ".md", ".txt", ".py", ".js", ".ts", ".json", ".yaml", ".yml", ".toml", ".csv", ".sh"}
SECRET_PATTERNS = {
    "private key": re.compile(r"BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "OpenAI-style key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "Slack token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    "authorization header": re.compile(r"Authorization:\s*Bearer\s+[A-Za-z0-9._~-]{16,}", re.IGNORECASE),
    "macOS private path": re.compile(r"/Users/(?!<|example|username)[A-Za-z0-9._-]+/"),
    "Windows private path": re.compile(r"[A-Za-z]:\\Users\\(?!<|example|username)[^\\\s]+\\"),
}
HIDDEN_CHARS = {"\u200b", "\u200c", "\u200d", "\u202a", "\u202b", "\u202d", "\u202e", "\u2066", "\u2067", "\u2068", "\u2069", "\ufeff"}
SENSITIVE_NAMES = {"config.yaml", "config.yml", ".mcp.json", "credentials.json", "cookies.txt"}
SENSITIVE_SUFFIXES = (".pem", ".key", ".p12", ".pfx")
EMAIL = re.compile(r"(?i)\b[A-Z0-9._%+-]+@([A-Z0-9.-]+\.[A-Z]{2,})\b")
ALLOWED_EMAIL_DOMAINS = {"users.noreply.github.com", "example.com", "example.invalid"}
MAX_BLOB_BYTES = 2_000_000


def iter_files(root: Path):
    for current, dirs, files in os.walk(root):
        current_path = Path(current)
        kept: list[str] = []
        for name in dirs:
            path = current_path / name
            if name in SKIP_DIRS:
                continue
            if path.is_symlink():
                yield path
            else:
                kept.append(name)
        dirs[:] = kept
        for name in files:
            yield current_path / name


def sensitive_name(name: str) -> bool:
    lower = name.lower()
    return lower in SENSITIVE_NAMES or lower == ".env" or lower.startswith(".env.") or lower.endswith(SENSITIVE_SUFFIXES)


def scan_text(text: str, label: str, findings: list[str]) -> None:
    for secret_label, pattern in SECRET_PATTERNS.items():
        if pattern.search(text):
            findings.append(f"{secret_label}: {label}")
    for match in EMAIL.finditer(text):
        if match.group(1).lower() not in ALLOWED_EMAIL_DOMAINS:
            findings.append(f"personal email address: {label}")
            break
    if any(char in text for char in HIDDEN_CHARS):
        findings.append(f"hidden Unicode control: {label}")


def run_git(root: Path, *args: str, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=text,
        check=False,
    )


def audit_git_history(root: Path, findings: list[str]) -> None:
    inside = run_git(root, "rev-parse", "--is-inside-work-tree")
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        findings.append("Git history unavailable for release audit")
        return

    metadata = run_git(root, "log", "--all", "--format=%H%x00%ae%x00%ce")
    if metadata.returncode != 0:
        findings.append("could not inspect Git commit metadata")
    else:
        for line in metadata.stdout.splitlines():
            parts = line.split("\x00")
            if len(parts) != 3:
                continue
            commit, author_email, committer_email = parts
            for value in (author_email, committer_email):
                match = EMAIL.fullmatch(value.strip())
                if match and match.group(1).lower() not in ALLOWED_EMAIL_DOMAINS:
                    findings.append(f"personal email in commit metadata: {commit[:12]}")
                    break

    tags = run_git(root, "for-each-ref", "--format=%(refname:short)%00%(taggeremail)", "refs/tags")
    if tags.returncode != 0:
        findings.append("could not inspect Git tag metadata")
    else:
        for line in tags.stdout.splitlines():
            tag_name, _, tagger = line.partition("\x00")
            match = EMAIL.search(tagger)
            if match and match.group(1).lower() not in ALLOWED_EMAIL_DOMAINS:
                findings.append(f"personal email in tag metadata: {tag_name}")

    objects = run_git(root, "rev-list", "--objects", "--all")
    if objects.returncode != 0:
        findings.append("could not enumerate reachable Git objects")
        return
    for line in objects.stdout.splitlines():
        object_id, _, object_path = line.partition(" ")
        if object_path and sensitive_name(Path(object_path).name):
            findings.append(f"sensitive filename in Git history: {object_path}")
        object_type = run_git(root, "cat-file", "-t", object_id)
        if object_type.returncode != 0 or object_type.stdout.strip() != "blob":
            continue
        size = run_git(root, "cat-file", "-s", object_id)
        try:
            blob_size = int(size.stdout.strip())
        except (TypeError, ValueError):
            continue
        if blob_size > MAX_BLOB_BYTES:
            findings.append(f"large Git blob requires manual review: {object_path or object_id[:12]}")
            continue
        blob = run_git(root, "cat-file", "-p", object_id, text=False)
        if blob.returncode != 0:
            continue
        try:
            text_value = blob.stdout.decode("utf-8")
        except UnicodeDecodeError:
            continue
        scan_text(text_value, f"Git blob {object_path or object_id[:12]}", findings)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument(
        "--working-tree-only",
        action="store_true",
        help="Skip Git history; intended only while preparing an unreleased rewrite",
    )
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    findings: list[str] = []

    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 2

    for path in iter_files(root):
        relative = path.relative_to(root)
        if sensitive_name(path.name):
            findings.append(f"sensitive filename: {relative}")
        if path.is_symlink():
            findings.append(f"symlink requires manual review: {relative}")
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        scan_text(text, str(relative), findings)

    if not args.working_tree_only:
        audit_git_history(root, findings)

    if findings:
        for finding in sorted(set(findings)):
            print(f"ERROR: {finding}", file=sys.stderr)
        return 1
    print(f"public-release audit passed: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
