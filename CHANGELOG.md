# Changelog

## 0.2.1 - 2026-07-15

- Add a complete Traditional Chinese README, language navigation, status badges, and public contact routes.
- Enable GitHub Discussions and add Issue-routing and pull-request templates.
- Stop treating every generic `config.yml` or `config.yaml` filename as sensitive while continuing to scan its contents for secrets.
- Allow GitHub's documented noreply merge identity in PR merge refs without allowing arbitrary `github.com` addresses.
- Add regression tests for legitimate tooling configuration files and GitHub-generated merge commits.

## 0.2.0 - 2026-07-15

- Add native Codex, Claude Code, and Grok plugin metadata around one canonical Agent Skill.
- Make generated packages private by default with release approval gating.
- Separate structure, MVP, and release validation so empty skeletons cannot pass as complete systems.
- Audit the working tree, reachable Git history, commit metadata, sensitive filenames, personal email, hidden Unicode, and symlinks.
- Add cross-platform manifest consistency checks, trigger evaluations, and security regression tests.
