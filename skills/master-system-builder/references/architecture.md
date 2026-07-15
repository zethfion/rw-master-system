# Architecture and schemas

## Package structure

```text
<knowledge-root>/<expert-id>/
├── .master-system.json
├── README.md
├── soul.md
├── index.md
├── corpus/
│   ├── emails/
│   ├── books/
│   ├── articles/
│   ├── podcasts/
│   ├── youtube/
│   ├── courses/
│   ├── webinars/
│   └── other/
├── distillates/
├── frameworks/
├── examples/
├── evidence/
│   ├── sources.csv
│   ├── claims.csv
│   └── open-questions.md
├── consultations/
└── log.md
```

Keep source material private by default. A package may live in a private repository, an encrypted store, or outside version control. Do not assume the Skill repository is an appropriate data location.

## Source document frontmatter

```yaml
---
master: expert-id
title: "Source title"
source_type: youtube
source_url: "https://example.invalid/stable-source"
source_id: "provider-stable-id"
author: "Named author"
speakers:
  - "Speaker name"
published_date: 2025-01-15
collected_date: 2026-01-20
language: en
channel: youtube
register: conversational
evidence_level: primary
access_basis: public
transcript_method: official-caption
fidelity: reviewed
content_hash: "sha256:..."
tags:
  - topic-name
---
```

Use `null` for unknown values. Do not invent dates, speakers, or rights claims.

## Registers

- `doctrinal`: books, courses, or formal teaching; prioritize for methods.
- `conversational`: interviews, podcasts, and Q&A; prioritize for reasoning and natural voice.
- `performative`: ads, sales email, landing pages, and demonstrations; prioritize as craft examples rather than personality evidence.

## Evidence levels

- `primary`: the expert authored or personally stated it.
- `affiliated`: an official organization, staff member, school, or partner stated it.
- `secondary`: an independent reviewer or implementer stated it.
- `inferred`: the package builders derived it from identified evidence.
- `unknown`: the material does not establish it.

## Runtime retrieval

Use three levels:

1. Load all of `soul.md` because stable boundaries and reasoning should remain coherent.
2. Load selected framework cards by task.
3. Retrieve corpus excerpts only when a claim, example, or disputed detail needs evidence.

Start with directory structure and metadata, then full-text search, then semantic retrieval when necessary. Do not introduce a vector database unless the corpus and query behavior justify its operational cost.
