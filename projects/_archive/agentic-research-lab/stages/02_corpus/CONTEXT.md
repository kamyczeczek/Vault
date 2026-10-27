---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Stage 02_corpus — Corpus Chunks & Frontmatter Grounding

Source of truth for chunked scientific research notes.

## Inputs
- `knowledge/raw/*.md` (archived source documents)
- `knowledge/raw/manifest.jsonl` (raw-to-corpus mappings)

## Process
1. Validate that each file in `knowledge/corpus/*.md` maintains canonical frontmatter (`title`, `source`, `tags`).
2. Ensure tags adhere strictly to the controlled vocabulary in `knowledge/topics.md`.
3. Assert that corpus chunks match manifest entries 1:1.

## Outputs
- Canonical chunk files in `knowledge/corpus/*.md`

## Exit Gate
`python scripts/check_manifest.py` exit 0 (corpus chunks match manifest `corpus_ids` exactly).
