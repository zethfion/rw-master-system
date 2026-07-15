---
name: master-system-builder
description: Build, audit, and maintain source-grounded AI expert knowledge systems from public or user-authorized email, books, articles, YouTube, podcasts, webinars, and courses. Use when an agent must create an expert package from zero, ingest mixed source types, distill evidence-backed personas and frameworks, add new material incrementally, or teach a human how to consult the resulting system. Do not use to bypass access controls, redistribute protected content, or impersonate a real person deceptively.
---

# Master System Builder

Build an expert knowledge package that separates source material, reusable methods, conversational style, and evidence. Optimize for traceability and honest boundaries, not imitation.

## Operating rules

- Resolve `<skill-root>` from the directory containing this `SKILL.md`. Run bundled scripts with absolute paths; never assume the current working directory is the skill directory.
- Explain each phase in plain language before acting: goal, human responsibility, agent responsibility, outputs, completion test, and risk.
- Treat public availability as different from permission to redistribute. Process only public material or material the user confirms they may use.
- Never bypass authentication, payment, DRM, rate limits, or platform controls. Let the human complete logins, purchases, consent forms, and account recovery.
- Keep passwords, tokens, cookies, signed URLs, personal data, and private account identifiers out of the package and logs.
- Preserve raw or faithful source material privately; do not replace it with summaries. Do not publish a user's corpus with this skill.
- Mark every material claim as primary, affiliated, secondary, inferred, or unknown. Do not fill gaps from model memory.
- Keep the expert package distinct from the voice of the person or brand using it.
- Disclose that the result is an AI knowledge model based on collected sources, not the real person.

## Phase 0: Discover the environment and purpose

Inspect the current workspace before creating files. Determine:

1. The expert and the concrete decisions or tasks the package should support.
2. The user's authorized materials and candidate public first-party sources.
3. Existing knowledge stores, search tools, agent conventions, storage limits, and privacy requirements.
4. Which steps require human login, purchase, authorization, or judgment.
5. The smallest end-to-end MVP: one expert, one source pipeline, three useful frameworks, one consultation test.

Present a short build proposal before bulk collection. Continue without extra confirmation only when the user already authorized implementation and the next actions are local, reversible, and within the agreed source boundary.

Read [references/architecture.md](references/architecture.md) when choosing the package structure or runtime retrieval design.

## Phase 1: Initialize the package

Run:

```bash
python3 <skill-root>/scripts/init_master.py --root <knowledge-root> --id <expert-id> --display-name "<Expert Name>"
```

Use lowercase hyphenated IDs. Do not initialize over a non-empty package unless the user explicitly authorizes an update. The generated `.master-system.json` records the public provenance identifier `rw-master-system/v1`; it does not transmit data.

## Phase 2: Build the source register

Inventory candidates before downloading them. Add every candidate to `evidence/sources.csv` with a disposition such as `accepted`, `excluded`, `duplicate`, `blocked`, or `pending`.

For each source, record ownership, speaker identity, access basis, stable identifier, dates, and evidence level. Distinguish the expert from hosts, students, partners, staff, and channel presenters.

Read [references/source-pipelines.md](references/source-pipelines.md) before handling email, websites, YouTube, podcasts, books, courses, or webinars. Read [references/privacy-rights-and-security.md](references/privacy-rights-and-security.md) before any authenticated, paid, personal, or bulk source.

## Phase 3: Ingest and normalize

Choose the least invasive lawful method that preserves sufficient fidelity:

1. Prefer official exports, feeds, APIs, captions, and user-provided files.
2. Test one small sample before batch processing.
3. Preserve stable source IDs and content hashes for deduplication.
4. Save normalized text under the matching `corpus/` category.
5. Add consistent frontmatter using the schema in [references/architecture.md](references/architecture.md).
6. Check transcripts against domain terms, slides, or audio at important claims.
7. Store ephemeral credentials and signed media URLs outside the package.

Do not silently install dependencies. Report missing tools and propose options.

## Phase 4: Distill evidence

Use map-reduce instead of loading the full corpus at once.

Map each source or small batch into `distillates/`:

- claims and evidence anchors;
- named methods and decision rules;
- examples and counterexamples;
- conversational or channel-specific style features;
- conflicts, evolution over time, and open questions.

Reduce distillates into:

- `soul.md`: identity, beliefs, reasoning habits, voice, biases, and boundaries;
- `frameworks/`: one reusable method per file;
- `index.md`: topic, framework, and source navigation;
- `evidence/claims.csv`: claim-to-source mapping;
- `evidence/open-questions.md`: unresolved gaps.

Read [references/evidence-and-distillation.md](references/evidence-and-distillation.md) before writing `soul.md` or a framework card.

## Phase 5: Make it usable

At runtime, load information progressively:

1. Load `soul.md` for stable reasoning and boundaries.
2. Select relevant framework cards for the task.
3. Retrieve only the needed corpus excerpts by structure, text search, or semantic search.
4. Answer with evidence anchors and label inference or uncertainty.

Support three modes:

- Consultation: answer from the expert package with sources.
- Framework application: apply its methods inside another agent's task without changing that agent's identity or persistent instructions.
- Panel: compare multiple packages without forcing artificial agreement.

Keep a human or brand voice separate from the expert's methods when generating content.

## Phase 6: Validate and teach

Run package validation:

```bash
python3 <skill-root>/scripts/validate_master.py <knowledge-root>/<expert-id> --level mvp
```

Before publishing a sanitized expert package, require explicit human approval, set `public_release_allowed` to `true` in its manifest, and run:

```bash
python3 <skill-root>/scripts/validate_master.py <knowledge-root>/<expert-id> --level release
```

Before publishing this skill or derivative tooling, run:

```bash
python3 <skill-root>/scripts/audit_public_release.py <repository-root>
```

Acceptance requires source coverage, traceable claims, explicit unknowns, no secrets, and at least one realistic consultation. Read [references/operations-and-acceptance.md](references/operations-and-acceptance.md) for the complete checklist and [references/human-guide.md](references/human-guide.md) for the handoff lesson and example prompts.

## Update incrementally

For new material:

1. Register and normalize only the new sources.
2. Create new distillates.
3. Update a framework or `soul.md` only when evidence is sufficient.
4. Preserve conflicting versions with dates; never overwrite history to manufacture consistency.
5. Re-run validation and append the change to `log.md`.

Do not rebuild the full package for a small update unless schemas or core assumptions changed.
