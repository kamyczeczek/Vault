---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# CONTEXT.md — brain

One job: give a project a queryable index of its own sources, and prove the index
is a faithful derivation of those sources.

## Inputs

- Working (this run): the target project's markdown and Python sources
- Working (this run): raw INBOX material, for ingestion
- Reference (every run): `../../_archive/agentic-research-lab/CONTEXT.md` — chunk format and the
  extraction rules this follows

## Process

1. **Extract.** `bootstrap_project_brain.py` globs the project's `*.md` and
   `*.py` into atomic chunks; `ingest.py` handles raw INBOX documents.
2. **Normalize.** Extraction mode is chosen per page by measuring it, not by
   defaulting. Layout mode removes the intra-word whitespace that the default mode
   discards — a chunk with `Sys tem` in it indexes as two tokens and poisons
   every later retrieval.
3. **Index.** Chunks load into an FTS5 SQLite graph with typed frontmatter.
4. **Verify.** Rebuild twice and diff. A graph that varies run to run is not
   usable as a baseline.

## Outputs

- `.brain/corpus/NN_<slug>.md` — one chunk per file, with frontmatter
- `.brain/graph/graph.db` — the FTS5 index and its digest
- `.brain/graph/.graph_fingerprint` — the hash a downstream result pins against

## Human check

Take three questions whose answers you already know from the sources and query
them. If the brain returns front matter, a title page, or a glued token instead
of the passage, the extraction is damaged — fix the extractor, not the query. A
brain that confidently returns the wrong passage is worse than no brain, because
the caller cannot tell.

## Why the fingerprint matters

Downstream experiments pin a fingerprint before a run and refuse to compare
against a graph that has moved. This is what makes "the corpus was unchanged"
a checkable claim rather than an assertion. The fingerprint is satisfied by any
self-consistent graph, including a non-deterministic one — which is why
determinism is verified by building twice and diffing, and not by the hash.

## Known defect classes

| Defect | Symptom | Guard |
|---|---|---|
| Whitespace loss in extraction | `Sys tem`, `man-monthmythical` | measure glue runs per page |
| Front matter ingested as content | a "gold" chunk is a copyright page | check the chunk is a passage |
| Fabricated tags | FTS hits that no source supports | tags must come from frontmatter |
| Duplicate ingestion | `00_`/`01_` pairs of the same book | `../research-engine` duplicate scan |
| Non-determinism | same corpus, different graph | build twice and diff |

## Open work

**RESOLVED 2026-09-27: fingerprint is written.** `rebuild_graph()` in
`scripts/ingest.py:163-165` writes `.graph_fingerprint` alongside `graph.db`.
Prior stale claim fixed.

**The determinism guard has no harness.** CONTEXT.md requires building the
graph twice and diffing. No test, script, or CI step does that. Guarding
non-determinism is a manual instruction, not a check.

**`ingest.py` does not do the normalizing this file promises.**
`extract_text()` has exactly two modes — strip `.md` frontmatter, or take the
text as-is. There is no measured layout mode, so the `Sys tem` glue-run defect
in the table above is still live for INBOX PDFs, where `pypdf` extraction is
what produces the glue. It only reads `INBOX/*`; `bootstrap_project_brain.py`
in `../../_archive/agentic-research-lab` is the one that measures per page.

**`ingest.py` is a subset of the reference implementation.** It ingests
`*.md`, `*.txt`, `*.epub` and PDFs; the reference pipeline this project defers
to handles more formats. Also unimplemented: the duplicate-ingestion scan that
the defect table assigns to `../research-engine`, and the `rebuild twice and
diff` check.

**Ingest edges, all real.** A PDF that fails extraction is not skipped — it
becomes one chunk whose body is the literal string `[pdf extraction failed: …]`
(relying on `pypdf`, an undeclared import), which then indexes and retrieves as
if it were content. A failed run still leaves already-moved files in `INBOX/raw`.
`--file` resolves against `INBOX/` but silently accepts an absolute path
anywhere, so a stray path ingests outside the project. Untagged documents are
given a synthetic `["inbox", <stem>]` tag rather than an empty list, which hides
the "no tags" case from any audit.

**RESOLVED 2026-09-27: `ask.py` fallback is visible.** `except` prints
`NOTICE: FTS5 query failed … falling back to LIKE` on stderr and labels
results as LIKE fallback in stdout (visible in the return, not just console).

**No query, ranking, or filtering controls.** `--limit` is the only knob. There
is no tag filter, no source filter, no pagination, no field weighting, and no
graph traversal — the name "knowledge graph" oversells it; the FTS5 table is
five flat text columns with a `snippet()` projection.

**Not exercised against its own claim.** Per the Human check above, three
questions with known answers should be run against this brain. That has not
been done since `ingest.py` and `ask.py` were last written.
