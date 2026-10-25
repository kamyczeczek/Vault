---
type: Concept
flag: test-memory-index-format-restored-2026-10-23
since: 2026-10-23
owner: opencode
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: stale test imports after the 2026-10-21 memory_index restructure
title: test-memory-index-format-restored-2026-10-23
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`test-memory-index-format-restored-2026-10-23` — 2026-10-23: **`test_memory_index.py` is green (33/33).** The 2026-10-21 restructure removed `format_results`, `format_brief`, `get_chunk` and `print_usage` from `memory_index.py` but left the regression file importing them, so the suite died at import and its four guards were dead. Restored all four helpers and wired them back into `query --full` / default `query`, `get`, and `stats --usage`; `--with-context` now renders again as `(+Nctx)` in the brief view, which the inline rewrite had silently dropped.

Evidence:
- `scripts/memory_index.py` — `format_results`, `format_brief`, `get_chunk`,
  `print_usage`; `query` prints the brief/full views, `get` drills via
  `get_chunk` (None → exit 1), `stats --usage` delegates counts/window/terms to
  `print_usage` and keeps the usage-rate metrics.
- `scripts/test_memory_index.py` — CLI miss checks read `main()`'s return value
  (`main` returns int; it does not raise `SystemExit` on a miss).
- `python.exe scripts/test_memory_index.py` — 33/33, all checks passed.
- `check_workspace_integrity.py` — OK; freshness OK; retrieval_eval hit@5=1.000
  MRR=0.577; drift OK (10 stores).

not checked: the `format_results` body path prefers a real `snippet` key and
otherwise falls back to the 400-char `_evidence_snippet`, so its per-hit cost is
unchanged from the inline version; no end-to-end `--rebuild` cost measured.
