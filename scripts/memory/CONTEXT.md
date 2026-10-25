---
type: Concept
name: session-memory
folder: scripts/memory
form: record-library
job: recall — what earlier agents already tried, decided and broke
unit: one session (record), accumulating in the agent's own store
owner: every agent in the root workspace
derived: scripts/_scratch/sessions/05_store/memory.db (gitignored, rebuildable — never hand-edit)
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:28Z }
---

# Session memory — contract

## Recall — which command

`memory_index.py query` (default) searches **session transcripts only** — it excludes
`chunk_type='curated'` (SCARS.md, DECISIONS.md, handoff/CONTEXT.md, ...). To recall a
**scar or a decision**:

- `python.exe scripts/memory_index.py query "<query>" --type curated --limit 10`
  — forces the curated pool; returns the **chunk** holding the scar (e.g. `SCA::30`),
  then drill with `get <chunk_id>`. Works only on a **fresh** shelf: SCARS.md is
  re-chunked by `memory_index.py ingest`, so a stale shelf answers with the file
  header (`SCA::0`) or nothing at all.
- `python.exe scripts/debug.py "<query>"` — the door; recalls **sessions**. The
  curated shelf is pinned only when bm25 already returned it, which its 3-token
  `AND` query usually does not, so the **default** is not a scar-recall tool (S77).
  With `--type curated` it calls `query_memory(chunk_type_filter='curated')` — the
  same call as the line above, so `debug.py "<query>" --type curated` **is**
  equivalent (S79).

A query that returns zero hits for a known scar (S73/S75) is a **method error** —
check the command *and* the shelf's freshness before concluding "regression"
(S76/S77).

## What this is

A **record library** (ICM form 3). The record is a *session*; records accumulate in
six agent stores on this machine and are retrieved through one FTS5 index. Nothing
here runs to completion — this is lookup, not a production line. The only pipeline
is maintenance: ingest → index → query.

| Part | Path | Role |
|---|---|---|
| Loaders (factory) | `scripts/agent_sessions.py` | one reader per agent store: opencode, goose, hermes, pi, jcode, antigravity |
| Index (this folder's job) | `scripts/memory_index.py` | `ingest` / `query` / `get` / `stats` / `freshness` |
| Store (product, derived) | `scripts/_scratch/sessions/05_store/memory.db` | 650 sessions, 100 173 chunks as of 2026-10-05; gitignored, rebuildable |

**Durable meta-session exclusions.** `memory_index.EXCLUDED_SESSION_IDS` holds
the sessions about the export/index machinery itself (they re-state the eval's
query terms and dropped retrieval 15/15 → 13/15 on 2026-10-23). `ingest` skips
them and purges any rows already in the derived store; `freshness` and
`memory_index_check_drift.py` skip them when asking what is on disk. The store
stays derived: the checked-in list is the source, the DB is rebuilt from it.
Add an id with a one-line reason and re-run `eval_memory_retrieval.py` before
removing one.

Holds four chunk types, and the type is the first filter to reach for:
`error` (12 129 — a failure and its traceback), `decision` (3 771 — a choice with
its rejected options), `content`, `tool`.
*(Note on `decision`: The classifier relies on a broad regex of keywords like "Solution" or "fixed". A manual audit of all 76 tool-associated decision chunks (lines 1-790) found only 3/76 uncleaned tool fragments (e.g. from missed `## [tool]` headers or section inheritance). The remaining 73/76 are genuine conversational text where the agent naturally used these words. This establishes an inherent baseline of conversational FPs when filtering by `--type decision`.)*

## When you MUST query it

This is the whole point of the folder, and the honest limit of it: **the trigger is a
convention, not an automatic call.** Nothing invokes this index — no hook, no
pre-flight step, no gate that can see a failure you have not described yet. An agent
that never opens this file never queries it, and no check in this repo will notice.
That is the same bargain as `gate_has_no_automatic_caller`: the gate has no caller
either, and is run by hand before a commit. What this buys is that an agent *can*
decide from `AGENTS.md` alone, without being told; what it does not buy is that it
*will*. Read the triggers as binding on you, and treat a skipped query on a matching
trigger as the bug — not as an absence of one.

1. **Before fixing a failure you did not author** — a traceback, a failing test, a
   flaky timeout, a tool that "does not work". The question is *has this already
   happened here, and what did it turn out to be?*
2. **After the second failed attempt at the same operation.** Two failures means the
   fix is not local; the recorded past is cheaper than a third guess.
3. **Before a structural change to the root** — a new gate rule, a new root entry, a
   new process step. The scars live in past sessions and in `DECISIONS.md`; a rule
   invented twice is the failure this prevents.
4. **When asked "what did we already try" or "why is it like this".** `HANDOFF.md`
   holds the present; the *rejected attempts* live only in transcripts.

**Anti-triggers** — do not query for these:

- Current state of the work → `HANDOFF.md` / `STATE.md` own that (one home per fact).
- Before a first cheap attempt at anything. The index is keyword-matched, ~30 days
  deep, and cannot reason; it is a memory for *recurrence*, not a planner.
- Deep history older than the current corpus → `python scripts/memory_index.py ingest --days 90`.

## How to query — survey, then drill, never slurp

```bash
# 1. survey: one line per hit. This is the default — the cheap path is the safe one.
python scripts/memory_index.py query "cache hit ratio" --limit 8
python scripts/memory_index.py query "gate exit 1" --type error --agent goose

# 2. drill: pay for the one hit worth reading.
python scripts/memory_index.py get opencode::ses_efc4a483::31

# 3. widen: the whole session, when the chunk is a pointer into it.
python scripts/agent_sessions.py export opencode ses_efc4a4835ffeifkMuP7RIXM445 -o %TEMP%\s.md
```

Run these with the Windows interpreter (`python.exe`). Under this repo's MSYS shell
`python3` is WSL's, where `Path.home()` is /home/<user>, no agent store resolves, and
`freshness` correctly refuses to pass.

Terms are AND-ed FTS5 tokens, falling back to OR only when AND finds nothing, so
**more words = narrower** ("git diff whitespace check": 49 hits, not 10 173). A query
too specific for AND still returns the broad sweep rather than a false "nobody has hit
this" — so a zero-hit result means *no chunk holds all of it*, and the fix is a
narrower query, never a stale index. Start with the two or three tokens that would
appear in the transcript (`--check`, `CRLF`, `bm25`), not a sentence. Use
`--type error` when hunting a failure and `--type decision` when hunting a choice.
`--full` prints a 400-char evidence paragraph per hit (~15 lines each) and is opt-in:
the default survey costs ~10 lines instead of ~120.

## Usage telemetry

Every `query` and `get` appends one JSON line to
`scripts/_scratch/sessions/05_store/queries.jsonl` — the gitignored twin of
`memory.db`: timestamp, command, parameters, and the outcome (hit count
for a `query`, `found` for a `get`). A zero-hit query and a `get` of a
dead chunk id are logged too. The trigger stays a convention — nothing
*invokes* this index — but the gap is now visible: a skipped query does
not merely leave no trace of having happened, and a mis-drilled one
leaves a `found: false` line instead of silence.

Read it: `python.exe scripts/memory_index.py stats --usage` (event
counts, zero-hit rate, window, top terms). Telemetry is observability,
not a load-bearing path — a failed append warns on stderr and the
command still runs.

## Maintenance — the part that runs without you

| When | Command | Check |
|---|---|---|
| Once a working day, or when R14 fails | `python.exe scripts/memory_index.py ingest` | `python.exe scripts/memory_index.py freshness` → `OK` |
| After changing a chunking rule | `python.exe scripts/memory_index.py ingest --rebuild` | `stats` counts move as expected |
| Schema/tokenizer change | `ingest --rebuild` | the db is derived; a stale shape is worse than a slow one |
| Health at any time | `python.exe scripts/memory_index.py stats` | — |
| Read the usage trace | `python.exe scripts/memory_index.py stats --usage` | — |

`scripts/memory_index.py freshness` re-derives every readable session from the
agents' own stores, compares per-agent counts with `sessions_meta`, and compares
the newest dates; it exits 1 on a coverage gap or when the index is more than
`--max-lag-hours` (default 24) behind. The gate runs it as **R14**.

The tolerance is deliberate: the session being written right now is always newer than
the last ingest, so an equality rule would fail every commit.

**`python.exe`, not `python3`, on this machine.** In this repo's MSYS shell `python3`
is WSL's interpreter: `Path.home()` is `/home/<user>`, no agent store resolves, and
`freshness` used to answer `OK — no agent stores readable` with exit 0 — a green that
verified nothing. It now answers `UNVERIFIED` and exits 1, because the index
demonstrably holds sessions for stores this interpreter cannot see. Read an `OK` from
`freshness` as "the comparison ran", never as "there is nothing to check".

## Human check

After any `ingest`, `python scripts/memory_index.py query "<a phrase you know is in
the corpus>"` and confirm the expected session appears. An ingest that
reports 61 000 chunks and cannot find the session you just finished is a silent
failure; the count is not the proof.

## Failure modes seen in the wild

- **Trusting an empty result.** A stale index answers "nobody ever hit this"
  confidently. That is what R14 exists for — a missing memory reads as a false claim.
- **Reading the whole session to answer one question.** `get <chunk_id>` first; the
  export is the last resort, not the first.
- **Treating this contract as automation.** Nothing calls it. An agent that skipped
  the query leaves no trace, and no gate here can tell. The trigger is a promise the
  agent makes to itself, and the only enforcement is that it wrote it down.
- **Ingest cadence vs. `--days`.** The window is a floor on *recall*, not a cap on
  growth; a 30-day window means "recent scars are findable", and widening it is a
  deliberate act (66 MB db, ingest is not free).
- **The db is derived.** Never edit it, never commit it, never treat it as the
  source of truth about what a session said — the transcript at `raw_path` is.

## Related, do not duplicate

Present state → `HANDOFF.md`, `STATE.md`. Why the workspace looks like this →
`DECISIONS.md`. Session inventory and HTML browsing →
`scripts/agent_sessions.py browse`. Session transcripts as markdown (what a human
reads when a chunk is not enough) → the same script's `export`.
