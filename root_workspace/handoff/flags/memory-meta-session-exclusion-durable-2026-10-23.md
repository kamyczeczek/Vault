---
flag: memory-meta-session-exclusion-durable-2026-10-23
since: 2026-10-23
owner: opencode
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: memory-index meta-session regression (A workaround, B durable fix)
---

`memory-meta-session-exclusion-durable-2026-10-23` — 2026-10-23: **B landed;
A is durable.** `memory_index.EXCLUDED_SESSION_IDS` is the checked-in list; it
holds the four meta-sessions A removed plus this implementation session (that
session took #1 in two eval queries; without it MRR was 0.577 → 0.562).
`ingest` skips the list and purges any rows already in the derived store;
`freshness` and `memory_index_check_drift.py` filter it before asking what is
on disk. The first ingest after the change purged the implementing session and
reported "5 durably excluded"; drift OK (10 stores), freshness OK,
`retrieval_eval` 15/15 MRR 0.577.

Evidence:
- `scripts/memory_index.py` — `EXCLUDED_SESSION_IDS`, `is_excluded`,
  `filter_excluded`, `purge_excluded`; applied in `ingest` and `freshness`.
- `scripts/memory_index_check_drift.py` — `load_sessions_like_ingest` returns
  `memory_index.filter_excluded(sessions)`; the docstring names the policy.
- `scripts/test_memory_index_exclusions.py` — 5/5 (list, filter, purge,
  idempotence, freshness ignores an excluded newest).
- `scripts/test_memory_index_check_drift.py` — 9/9 (added the exclusion check).
- `scripts/memory/CONTEXT.md` — contract note.

Retires `handoff/flags/memory-index-meta-session-exclusion-2026-10-23.md` (A's
per-run workaround): the list is now the source, the DB is rebuilt from it.

not checked: the list is ID-based, so a new meta-session needs an id added (the
title scan found many close-out/instruction sessions; only the ones that
measurably displaced eval entries were excluded); full `--rebuild` cost
after B not measured.
