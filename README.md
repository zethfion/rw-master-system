# RW Master System

RW Master System is an open Agent Skill and plugin for building private, source-grounded AI expert knowledge systems from public or user-authorized materials. The same canonical skill works in Codex, Claude Code, and Grok; each platform receives only a thin native manifest.

It teaches an agent to inventory sources, preserve evidence, distill reusable frameworks, create an honest expert profile, and teach a human how to use the result. It ships the method, templates, and offline validation tools—not anyone's private corpus.

## What this repository contains

- `skills/master-system-builder/SKILL.md`: the reusable agent workflow.
- `skills/master-system-builder/references/`: detailed source, evidence, safety, and operations guidance.
- `skills/master-system-builder/scripts/`: deterministic local initialization and validation tools.
- `skills/master-system-builder/assets/`: empty templates copied into a new expert package.
- `.codex-plugin/`, `.claude-plugin/`, and `plugin.json`: native distribution metadata.
- `evals/` and `tests/`: trigger cases, privacy regressions, and deterministic validation.

## What it never contains

- Private email, paid course material, book text, or real consultation logs.
- Tokens, cookies, credentials, signed URLs, or account identifiers.
- A prebuilt imitation of a real person.
- Telemetry or hidden network callbacks.

## Install the v0.2.0 plugin

### Codex

```bash
codex plugin marketplace add zethfion/rw-master-system --ref v0.2.0
codex plugin add rw-master-system@rw-master-system
```

Start a new Codex task, then invoke `$master-system-builder` or describe the expert-system task naturally.

### Claude Code

```bash
claude plugin marketplace add zethfion/rw-master-system
claude plugin install rw-master-system@rw-master-system
```

Start a new Claude Code session. Invoke `/rw-master-system:master-system-builder` or describe the task naturally.

### Grok

```bash
grok plugin install zethfion/rw-master-system@v0.2.0
```

Start a new Grok session. Invoke `/master-system-builder` or describe the task naturally.

## Install only the standalone skill

Copy the entire `skills/master-system-builder` directory, including its `LICENSE`, into one of these discovery roots:

- Codex: `${CODEX_HOME:-$HOME/.codex}/skills/`
- Claude Code: `~/.claude/skills/`
- Grok: `~/.grok/skills/` or `~/.agents/skills/`

Do not copy only `SKILL.md`; the workflow depends on its bundled scripts, references, assets, and canonical `VERSION` file.

## Quick start

Example request:

```text
Use $master-system-builder to help me build a private expert knowledge system for <name>. Start with a Phase 0 proposal. I have permission to use these materials: <links or paths>. The system should help me with <concrete purpose>.
```

The skill begins with a small proposal and source boundary. It does not bulk-download material or cross authentication boundaries without the user's authorization.

Bundled scripts are resolved relative to the installed skill directory, so they work regardless of the caller's current working directory.

## Validation levels

```bash
python3 /path/to/master-system-builder/scripts/validate_master.py /path/to/expert-package --level structure
python3 /path/to/master-system-builder/scripts/validate_master.py /path/to/expert-package --level mvp
python3 /path/to/master-system-builder/scripts/validate_master.py /path/to/expert-package --level release
```

- `structure` verifies schemas, required paths, version provenance, and privacy defaults.
- `mvp` also requires accepted local evidence, traceable claims, three sourced frameworks, explicit unknowns, and a consultation example.
- `release` additionally requires an explicit `public_release_allowed: true` gate and rejects private corpus directories, secrets, personal email, hidden controls, and symlinks.

Freshly initialized packages pass only `structure`; an empty skeleton is not reported as a finished MVP.

## Privacy model

Generated packages include a private-by-default `.gitignore`, `PRIVACY.md`, disabled network telemetry, and `public_release_allowed: false`. Changing that flag is a human approval step, not an automatic publication action.

## Provenance

Packages initialized by the included script contain the transparent identifier `rw-master-system/v1` and generating skill version `0.2.0`. This is a public origin marker, not tracking: no usage data leaves the user's machine.

## License

MIT. See `LICENSE`.
