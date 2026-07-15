#!/usr/bin/env python3
"""Validate cross-platform manifests and release metadata."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_NAME = "rw-master-system"
SKILL_NAME = "master-system-builder"


def load_json(path: Path, errors: list[str]) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
        return {}


def main() -> int:
    errors: list[str] = []
    version = (ROOT / "skills" / SKILL_NAME / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        errors.append("VERSION must contain strict semantic versioning")

    manifest_paths = (
        ROOT / ".codex-plugin" / "plugin.json",
        ROOT / ".claude-plugin" / "plugin.json",
        ROOT / "plugin.json",
    )
    manifests: list[dict[str, object]] = []
    for path in manifest_paths:
        value = load_json(path, errors)
        if not isinstance(value, dict):
            errors.append(f"manifest must be an object: {path.relative_to(ROOT)}")
            continue
        manifests.append(value)
        if value.get("name") != PLUGIN_NAME:
            errors.append(f"manifest name mismatch: {path.relative_to(ROOT)}")
        if value.get("version") != version:
            errors.append(f"manifest version mismatch: {path.relative_to(ROOT)}")
        if value.get("license") != "MIT":
            errors.append(f"manifest license mismatch: {path.relative_to(ROOT)}")
        author = value.get("author")
        if not isinstance(author, dict) or not author.get("name"):
            errors.append(f"manifest author missing: {path.relative_to(ROOT)}")
        elif "email" in author:
            errors.append(f"public manifest must not contain author email: {path.relative_to(ROOT)}")

    codex_market = load_json(ROOT / ".agents" / "plugins" / "marketplace.json", errors)
    claude_market = load_json(ROOT / ".claude-plugin" / "marketplace.json", errors)
    for label, market in (("Codex", codex_market), ("Claude", claude_market)):
        if not isinstance(market, dict):
            errors.append(f"{label} marketplace must be an object")
            continue
        plugins = market.get("plugins")
        if not isinstance(plugins, list) or len(plugins) != 1 or not isinstance(plugins[0], dict):
            errors.append(f"{label} marketplace must contain exactly one plugin entry")
            continue
        entry = plugins[0]
        if entry.get("name") != PLUGIN_NAME:
            errors.append(f"{label} marketplace plugin name mismatch")
        if label == "Claude" and entry.get("version") != version:
            errors.append("Claude marketplace version mismatch")
    if isinstance(codex_market, dict):
        entry = (codex_market.get("plugins") or [{}])[0]
        source = entry.get("source") if isinstance(entry, dict) else None
        if not isinstance(source, dict) or source.get("ref") != f"v{version}":
            errors.append("Codex marketplace release ref mismatch")

    skill_files = list((ROOT / "skills").glob("*/SKILL.md"))
    if skill_files != [ROOT / "skills" / SKILL_NAME / "SKILL.md"]:
        errors.append("distribution must contain exactly one canonical SKILL.md")
    else:
        text = skill_files[0].read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
        if not match:
            errors.append("SKILL.md frontmatter is missing")
        else:
            keys = [line.split(":", 1)[0].strip() for line in match.group(1).splitlines() if ":" in line]
            if keys != ["name", "description"]:
                errors.append("SKILL.md frontmatter must contain only name and description")
            if f"name: {SKILL_NAME}" not in match.group(1):
                errors.append("SKILL.md name mismatch")

    if (ROOT / "LICENSE").read_bytes() != (ROOT / "skills" / SKILL_NAME / "LICENSE").read_bytes():
        errors.append("root and standalone-skill LICENSE files differ")

    for relative in ("README.md", "README.zh-TW.md", "PROVENANCE.md", "CHANGELOG.md"):
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing distribution document: {relative}")
            continue
        if version not in path.read_text(encoding="utf-8"):
            errors.append(f"distribution version missing from {relative}")
    if "README.zh-TW.md" not in (ROOT / "README.md").read_text(encoding="utf-8"):
        errors.append("English README must link to the Traditional Chinese README")
    if "README.md" not in (ROOT / "README.zh-TW.md").read_text(encoding="utf-8"):
        errors.append("Traditional Chinese README must link to the English README")

    evals = load_json(ROOT / "evals" / "cases.json", errors)
    if not isinstance(evals, dict) or evals.get("schema") != "rw-master-system/evals/v1":
        errors.append("evals/cases.json schema mismatch")
    else:
        cases = evals.get("cases")
        if not isinstance(cases, list) or len(cases) < 6:
            errors.append("at least six trigger evaluation cases are required")
        elif {case.get("should_trigger") for case in cases if isinstance(case, dict)} != {True, False}:
            errors.append("evaluation cases must include positive and negative triggers")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"distribution valid: {PLUGIN_NAME} v{version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
