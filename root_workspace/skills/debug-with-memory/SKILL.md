---
name: debug-with-memory
description: "Debug an unfamiliar error, failed command, flaky timeout, or 'this broke and I do not know why' by first querying the shared session-memory index for a past root cause, then drilling into the one hit worth reading. The door onto the workspace's own past: extract 2-3 tokens from the failure, `python.exe scripts/debug.py \"<error>\"` (or the survey-then-drill pair under it), apply if it matches, and record whether it helped. Use on ANY failure you did not author, after a second failed attempt at the same operation, and before a structural root change."
disable-model-invocation: true
---

# Debug with memory

A workspace with a memory is a library. This skill is the **door** (when to walk
in), the **librarian** (the walk inside), and the **loan log** (the trace it
leaves). Today the loan log exists but nothing forces a visit — that is the gap
this skill closes. It does not make the visit automatic (no harness hook can see
a failure you have not described yet); it makes the visit *cheap enough that the
right move becomes the obvious move*, and it makes the skipped visit *measurable*.

The index is keyword FTS5 over ~650 past agent sessions plus a small shelf of
curated lessons (`error` / `decision` / `content` / `tool` / `curated`). It is a
memory for **recurrence**, not a planner: it answers "has this already happened
here, and what did it turn out to be?", and it cannot reason.

## When to open the door

Binding triggers (from `scripts/memory/CONTEXT.md` §When you MUST query it):

1. **A failure you did not author** — a traceback, a failing test, a flaky
   timeout, a service that "is unavailable". The question is: *has this already
   happened here?*
2. **A second failed attempt at the same operation.** Two failures means the fix
   is not local; the recorded past is cheaper than a third guess.
3. **Before a structural root change** — a new gate, a new root entry, a new
   process step. The scars live in past sessions and in `DECISIONS.md`; a rule
   invented twice is the failure this prevents.
4. **"What did we already try / why is it like this?"** `HANDOFF.md` owns the
   present; the rejected attempts live only in transcripts and the index.

Anti-triggers — do not open the door for: current state (that is `HANDOFF.md` /
`STATE.md`), a first cheap attempt at anything, or history older than the corpus.

## The walk — seven steps, no slurping

```
1  Agent hits an error / unknown situation
2  Extract 2-3 tokens from the message (identifiers + codes, not a sentence)
3  Query:  python.exe scripts/debug.py "<error string>"
           (thin wrapper over the survey-then-drill pair, below)
4  Get 1-5 candidates, one line each: chunk_id + session date + [type] + heading
5  Drill:  python.exe scripts/memory_index.py get <chunk_id>   # top 1-2 only
6  Apply the past fix — OR note the gap in the flag file
7  Record the outcome (helped / not-helped / gap) via the wrapper
```

The wrapper is the cheap default; use the raw pair when you need to control type
or agent filters:

```powershell
# survey (one line per hit) then drill (pay for the one worth reading)
python.exe scripts/memory_index.py query "workspaceController unavailable" --type error --limit 5
python.exe scripts/memory_index.py get droid::<id>::31
```

**Run with `python.exe`, not `python3`.** In this repo's MSYS shell `python3` is
WSL's, `Path.home()` is `/home/<user>`, no agent store resolves, and the query
returns nothing that looks like a real answer. `python.exe` is the Windows
interpreter that can see the stores.

## How the wrapper picks tokens

From the error string, keep the highest-signal 2-3 tokens, in priority order:

1. **CamelCase / snake identifiers** — `workspaceController`, `dsh_trim`,
   `memory_index`. These are the strongest FTS5 signals.
2. **Hex / error codes** — `0xC0000142`, `3221225794`, `404`, `503`.
3. **Paths and file names** — `cordis.patch.yml`, `node_modules`, `.dsh`.
4. **3+ char English nouns** that survive a small stopword filter.

More words = narrower (AND-ed FTS5 falls back to OR only when AND finds
nothing), so **two or three tokens beat a whole sentence**. A zero-hit result
means *no chunk holds all of it*, not a broken index — drop the least-signal
token and retry once, then stop and note the gap.

## Record the outcome (the loan log)

`scripts/debug.py` appends one JSON line to
`scripts/_scratch/sessions/05_store/queries.jsonl` for every run — the gitignored twin of
`memory.db`. It logs the terms, the command, and the outcome:

- a hit you **applied** → `outcome: "helped"`
- a hit you **rejected** (wrong root cause) → `outcome: "wrong"`
- a **zero-hit** → `outcome: "gap"` (the index had no knowledge for this)

`python.exe scripts/memory_index.py stats --usage` then reports the zero-hit
rate, the dead-chunk list, and prevented-repeat. A skipped visit now leaves a
measurable absence instead of silence — the whole reason the log exists.

## Worked example (the 2026-10-06 DSH gateway incident)

Symptom: `workspace create failed: gateway/service-unavailable: active Service
"workspaceController" is unavailable` after installing DSH plugins.

```powershell
python.exe scripts/debug.py "workspaceController is unavailable typert gateway"
```

Tokens the wrapper keeps: `workspaceController` `unavailable` `typert`
(identifiers + the strongest nouns). Top hit points at the past session where
the same service died after a plugin install left the profile in a half-built
state — the fix was restoring `package.json` to `dependencies: {}`, `cordis.yml`
to `[]`, and removing the leftover `node_modules/` + `pnpm-lock.yaml` before
relaunching. Apply, then:

```powershell
python.exe scripts/debug.py record helped "workspaceController is unavailable"
```

Next time the exact phrase surfaces, step 3 lands on the working fix instead of
re-diagnosing from scratch. That is the payoff the whole door is for.

## What NOT to do

- **Do not open the door for a first cheap attempt.** One `git status`, one
  `--help`, one read. The index is for recurrence, not exploration.
- **Do not slurp the session.** `get <chunk_id>` first; the `export` of the
  whole session is the last resort, not the first.
- **Do not trust a confident zero.** If `freshness` (R14) is failing, a zero-hit
  is a *stale index*, not "nobody has hit this" — ingest first, then re-query.
- **Do not invent the tokens.** If the error is a single opaque code you have
  not seen before, one narrowed query is the move; three blind ones is the loop
  this skill exists to stop.

## Related

The index and its contract: `scripts/memory/CONTEXT.md` (one home per fact —
this skill routes onto it, it does not restate it). The gate that keeps the
index fresh: R14 in `scripts/check_workspace_integrity.py`. The evaluation that
proves retrieval still works: `scripts/eval_memory_retrieval.py` (R15).
