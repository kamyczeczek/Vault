---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Stage 00_expand — Web Research & Inbox Broadening

Targeted web research to broaden knowledge coverage on specific topics or questions, depositing structured research notes into `INBOX/`.

## Inputs
- Topic or research query (e.g. from `knowledge/topics.md` or a seed brief in `INBOX/seeds/`)
- Existing knowledge graph: queried via `knowledge/graph/ask.py` to identify coverage gaps

## Process
1. Inspect current coverage using `python knowledge/graph/ask.py "<topic>"`.
2. Investigate primary sources (ArXiv papers, GitHub repositories, official documentation, authoritative technical discussions) using `skills/agent-reach` or `skills/research`.
3. Synthesize findings into an atomic research document adhering to the frontmatter schema:
   - `title`: descriptive human-readable title
   - `source`: primary web URLs consulted (e.g. `"web: https://arxiv.org/abs/... + https://github.com/..."`)
   - `tags`: relevant topic tags from `knowledge/topics.md`
4. Deposit the synthesized markdown file into `INBOX/<topic_slug>_web_research.md`.

## Outputs
- `INBOX/<topic_slug>_web_research.md` (un-ingested research note ready for phase 01)

## Invoke
```bash
python scripts/expand_topic.py "<topic or question>" [--tags t1,t2]
```

## Contract
- **Source attribution (Provenance invariant):** Every synthesized document must carry a non-empty `source:` frontmatter field listing the primary URLs consulted.
- **Controlled vocabulary:** Tags must align with `knowledge/topics.md`. If a new concept is discovered, register the tag in `knowledge/topics.md` first.
- **No ungrounded scraping:** Raw HTML dumps or noisy web pages must never be dumped directly into `INBOX/`; notes must be curated, structured markdown.
- **Determinism caveat:** The corpus fingerprint moves on every ingest. Read live from `knowledge/graph/.graph_fingerprint` — never hardcode it here.

## Handoff
Output files in `INBOX/` become the working input for `stages/01_inbox` (`python scripts/ingest.py`).
