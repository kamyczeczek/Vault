---
type: Concept
title: EXPERIENCE
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# EXPERIENCE.md — brain

Distilled on demand 2026-09-27 from `CONTEXT.md` Open work + `CLAUDE.md` Rules.
Each lesson names its evidence. Root links here (D11).

## Verified practices

1. **A brain is derived, always.**
   Corpus chunks, `graph.db`, fingerprint gitignored everywhere; rebuildable
   from the project or the project is missing sources. Evidence:
   `CLAUDE.md` Rules.
2. **One home per fact; cite a chunk, not a summary.**
   Same document indexed twice → two chunks, never a copied index; pass chunk
   ids onward, never surrounding prose. Evidence: `CLAUDE.md` Rules.
3. **Choose extraction mode per page by measuring it.**
   Default-mode PDF extraction discards glyph positioning (`Sys tem` → two
   FTS tokens; `man-monthmythical` → one). Reference implementation measures
   default vs layout per page. Evidence: `CONTEXT.md` Process §2.
4. **Determinism is build-twice-and-diff, never the hash.**
   The fingerprint is satisfied by any self-consistent graph, including a
   varying one. Evidence: `CONTEXT.md` "Why the fingerprint matters".
5. **Query with known-answer questions before trusting a brain.**
   Front matter / title page / glued token back means fix the extractor, not
   the query. A confident wrong passage beats no brain at being dangerous.
   Evidence: `CONTEXT.md` Human check.

## Known-unresolved (contract promises without mechanism)

- `.graph_fingerprint` documented in Outputs + `CLAUDE.md`, produced by no
  code here (`rebuild_graph()` writes only `graph.db`) — "corpus unchanged"
  currently unbacked.
- Determinism guard is a manual instruction; no test/script/CI builds twice
  and diffs.
- `ingest.py` has no measured layout mode (strip-frontmatter or as-is only),
  so the glue defect is live for INBOX PDFs; only reads `INBOX/*`; subset of
  the reference pipeline (no duplicate scan, no rebuild-diff).
- Failed PDF becomes a chunk containing `[pdf extraction failed: …]` and
  retrieves as content; failed run leaves moved files in `INBOX/raw`;
  `--file` accepts absolute strays; synthetic `["inbox", <stem>]` tags hide
  the untagged case.
- `ask.py`: raw user string into `MATCH ?` — prose queries throw on FTS5
  grammar, then silently fall back to 200-char `LIKE` prefix (front matter,
  title page, cut words); same `except` swallows missing/corrupt `graph.db`;
  absolute `path` strings unportable; `--limit` only knob (no tag/source
  filter, pagination, weighting, traversal — flat FTS5, not a graph).
- Human-check questions never run against this brain since last rewrite.

## Skills used

None vendored (D8 lazy).
