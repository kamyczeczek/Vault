---
ticket: E1
status: done
resolved: 2026-10-16
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
---

# E1 — schema-drift assertion per agent store

## What was built

One assertion, per agent store, owned by `scripts/memory_index_check_drift.py` and
called by `memory_index.py ingest` after it writes the index:

> the newest session a store **has on disk** is in the index (`sessions_meta`).

Definitions are fixed in the module docstring; the two failure modes are named
there: **silent skip** (raw store has ≥1 record, loader returned 0 — the S68
shape) and **drift** (newest loaded session absent from `sessions_meta`). The raw
probe never imports the production loader, so a loader that silently drops rows
cannot hide itself.

## Adversarial case (recorded BEFORE the run — S56/S62)

| # | mutation | expected behaviour before running |
|---|---|---|
| 1 | **shift** — inject a newer valid session into a store, re-ingest with `--exclude-session-id` so the loader sees it but the index does not | **FAIL**, exit 1, names store + expected tables/keys |
| 2 | **control** — clean `ingest` on the real corpus, then `--check` | **PASS**, exit 0 |
| 3 | **silent-skip shape** — store holds a file the loader cannot parse (deepseek `if not events: continue`) | **FAIL**, exit 1, named as silent skip — **not** a quiet skip |

The assertion is the thing under test: if it false-FAILs on the untouched real
corpus it is broken, so mutation 2 is the control for the other two.

## Result

All three mutations behaved exactly as recorded before the run.

### Mutation 2 — control (real corpus, clean ingest) → PASS

```
$ python.exe scripts/memory_index.py ingest
  Indexed: 2097 chunks from 10 new sessions
  Curated shelf: 491 chunks from the 6 root lessons + handoff/flags
  Drift  : memory_index drift: OK — 10 store(s) asserted, no drift
ingest_exit=0

$ python.exe scripts/memory_index_check_drift.py --check
OK   opencode     newest ses_ebd22e8e9ffeJnEf367F139OpB indexed (raw on disk: 465)
OK   goose        newest 20261011_1 indexed (raw on disk: 112)
OK   hermes       newest 20261002_154718_8be23e indexed (raw on disk: 189)
OK   pi           newest 01a14222-def4-72fd-bb75-9a78981ec516 indexed (raw on disk: 164)
OK   omp          newest 01a1291a-4efb-701d-8610-7105633d00d1 indexed (raw on disk: 600)
OK   jcode        newest session_zebra_1791741200509_745bf2ef1d7d55a8 indexed (raw on disk: 65)
OK   antigravity  newest f4030dcc-bf36-4cdb-910d-5c7229a731b0 indexed (raw on disk: 68)
OK   cursor       newest 1b5d6526-6009-44ba-970d-e3919867b7bb indexed (raw on disk: 521)
OK   droid        newest bc32b86f-1346-41a8-82cf-599c473ab0d3 indexed (raw on disk: 24)
SKIP deepseek     store present but empty on disk
OK   cline        newest session_1791685990953_19egx indexed (raw on disk: 15)
memory_index drift: OK — 10 store(s) asserted, no drift
exit=0
```

`deepseek` is SKIP because its standalone store is empty on this machine — its
data lives in `~/.dsh/sessions`, which `ingest` excludes as runtime. The
assertion skips an empty store rather than false-FAILing.

### Mutation 1 — shift (newer session injected, not indexed) → FAIL

Injected `~/.deepseek-harness/sessions/e1-shift-synth.jsonl` (a valid deepseek
session, mtime 2035), then re-ingested with `--exclude-session-id`:

```
$ python.exe scripts/memory_index.py ingest --exclude-session-id e1-shift-synth
  Indexed: 0 chunks from 0 new sessions
  ...
FAIL deepseek     drift — newest session 'e1-shift-synth' (C:\Users\Mateusz\.deepseek-harness\sessions\e1-shift-synth.jsonl) is not in sessions_meta; expected glob *.jsonl / *.zstd; dispatch keys type/data. Fix: python.exe scripts/memory_index.py ingest
memory_index drift: 1 FAIL, 11 store(s) asserted
  Drift  : FAILED — a store's newest session is missing from the index
ingest_exit=1
```

### Mutation 3 — silent-skip shape (unparseable file, loader drops it) → FAIL

Replaced it with `~/.deepseek-harness/sessions/e1-silent-skip.jsonl`
(`{"kind":"newformat",...}` — no `type`/`data`/`role` keys, so the loader's
`if not events: continue` drops it):

```
$ python.exe scripts/memory_index_check_drift.py --check
FAIL deepseek     silent skip — store holds 1 session record(s) on disk (glob *.jsonl / *.zstd; dispatch keys type/data) but the loader returned 0 sessions (S68 shape)
memory_index drift: 1 FAIL, 11 store(s) asserted
exit=1
```

### Restore

The synthetic file was removed; `~/.deepseek-harness/sessions` is empty again and
the control re-run returns `memory_index drift: OK — 10 store(s) asserted, no
drift` (exit 0).

### Did E1 find a real second S68?

No. On the real corpus all 10 stores that hold sessions resolve to an indexed
newest session; no loader silently dropped a non-empty store. No loader was
modified — the assertion detects, it does not repair.

## not checked

- SQLite stores (opencode/goose/hermes/cursor) were not mutation-tested; their raw
  probe is exercised only on the real corpus (the control). Mutations 1 and 3 ran
  on a directory store (deepseek).
- The "no index at all" path (`main` returns 1) was not run; only the path with an
  existing `memory.db`.
- R22 is wired **advisory** in the integrity gate; whether a hard wiring could
  avoid blocking commits made between a new session and the next ingest was not
  evaluated.
- The gate was **not** extended to check the reverse direction (a commit without a
  flag) — S71 records it as a candidate, not implemented here.
- `brain_eval.json` baseline metrics were not changed (hit 9/10, refusal 3/4,
  MRR 0.900; `expect_hash` untouched); the descriptive string "46 problems" was
  left as-is (rule 7) though `problems` is now 50 after S70/S71.
- Dług C: the full integrity output contains **no** `R18 governance streak:` line
  (only the two `R18: decision … PENDING_IMPLEMENTATION for 5d` warns), i.e. the
  streak is <3 — the E7 claim is confirmed raw. R18 itself was not changed.
- Pre-existing advisories untouched: two `MAP.md is stale` (knowledge-retrieval,
  the-pragmatic-programmer-retrieval) and the knowledge-retrieval `## Open work`.
