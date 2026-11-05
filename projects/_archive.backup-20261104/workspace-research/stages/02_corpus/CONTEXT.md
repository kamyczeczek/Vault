---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Stage 02_corpus — Canonical chunking. Single job: corpus markdown is source of truth.

This stage does one thing: deterministic `INBOX/` → `knowledge/corpus/` chunking.

## Budget
- `scripts/ingest.py:CHUNK_CHARS = 3000` — sections split at paragraph boundaries into ~3000-char parts (`split_sections`). Single fixed budget; files < budget stay as one chunk, files ≥ budget split into `NN_slug` parts.
- Per-source budget: implicitly governed by source length → count = ceil(body / CHUNK_CHARS), max parts seen 581 chunks from ~18 raw sources. Per-source caps stay implicit; budget is file-size, not chunk-count — add explicit caps in `ingest.py` if a source overgrows.

## Id Stability
- Chunk id = `NN_slug` where `NN` is total-sources padded index and `slug = slugify(source)` (first 48 chars, lowercased, non-alnum → `_`). Cross-run id is deterministic given sorted source order (`Path.glob` + `sorted` sources in `ingest.py`) and stable source filename. `total` in `"(part X/Y)"` title is total parts for that source; renumbering after source edit shifts later parts' running index.

## Inputs
- `INBOX/`
- `knowledge/raw/`

## Outputs
- `knowledge/corpus/*.md`

## Invoke
```
python scripts/ingest.py
```

## Contract
- **Manifest gate (exit condition):** every `knowledge/corpus/*.md` chunk must declare a
  `source:` frontmatter field, and every `knowledge/raw/` file must map to ≥1 chunk.
  Enforced by `python scripts/check_manifest.py` (exit 2 on break). The manifest is a
  DERIVED reverse index rebuilt from corpus `source:` fields — never hand-edited, never
  appended to; `scripts/ingest.py` rebuilds it on every successful run.
- Determinism: run is a no-op if the corpus fingerprint is unchanged. Read it live from
  `knowledge/graph/.graph_fingerprint` (or `GRAPH-DIGEST.md` line 1) — the value is
  `0626262b2982` at the time of writing, but it moves on every corpus edit, so never
  hardcode it here; a stale hardcoded value silently makes this contract lie.
- This stage's CONTEXT.md is the Inputs Table — the single disclosure level (one-level progressive disclosure).

## Handoff
Next stage consumes Outputs above via its own Inputs Table. The `.graph_fingerprint` + `GRAPH-DIGEST.md` fingerprint is the explicit handoff artifact for stage 03.
