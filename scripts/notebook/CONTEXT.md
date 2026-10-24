---
name: notebook-pipeline
folder: scripts/notebook
form: pipeline
job: run — push work state to NotebookLM, ask a defined problem, bring guidance back
unit: one run (pack + problem + answer, promoted or archived)
owner: every agent in the root workspace
derived: scripts/out/ (gitignored packs/sessions); handoff/notebook-runs/ (tracked runs)
---

# NotebookLM pipeline — contract

## What this is

A **pipeline** (ICM form 1). Each run pushes work state to the fixed notebook
`root_workspace` (`a49ff8cb-31e0-470e-b747-3f2a0ded1699`), asks one defined
problem, and brings the answer back as a tracked run. Factory lives in
`scripts/` (never move it — `notebook_push.py` does
`sys.path.insert(ROOT / "scripts")`); product lands in `scripts/out/` (derived,
gitignored) and `handoff/notebook-runs/` (primary, tracked).

| Part | Path | Role |
|---|---|---|
| Pack builder | `scripts/build_notebook_pack.py` | `--scope root/project`, `--level 0/1/2`, `--sessions N` |
| Pusher | `scripts/notebook_push.py` | `--auto` builds pack + exports sessions + `nlm source add` |
| Session reader | `scripts/agent_sessions.py` | per-agent exports feeding Shelf B |
| Auth | `nlm` CLI, profile `piwowarski` | CDP login; truth = `nlm doctor auth-replay` (`httpx_ok`) |
| Contract | this file | inputs, depths, run schema, promote rule |

## Depths (Q2 — conscious per-run choice)

| Question kind | Command |
|---|---|
| Debug / decision (default) | `--level 1 --sessions 5` |
| Structural audit / deep synthesis | `--level 2 --sessions 5` |
| "What did we do last week" | `--level 1 --sessions 15` |
| Project-scoped problem | `--scope project --project <name>` + root L0 as background |

Rationale: L1 (~16 KB summary) beats L2 (~232 KB full) for typical questions —
less noise, sharper citations. L2 is escalation, not default.

## Run schema (Q3 — tracked, because answers are primary)

`handoff/notebook-runs/<YYYY-MM-DD-slug>/`:

- `problem.md` — the defined problem (template: context / decisions to take /
  constraints). Uploaded as a source alongside the pack, so NotebookLM can cite it.
- `answer.md` — the raw `nlm query` answer **with citation numbers preserved**.
- Promotion happens within the same session (see below), never "later".

`scripts/out/` stays gitignored: packs and session exports are reproducible
derived artifacts. `problem.md`/`answer.md` are not reproducible (NotebookLM is
nondeterministic) — that is why the run folder is tracked and `out/` is not.

## Replace rule (prune — the notebook is a shelf, not an attic)

`--auto` prunes after a clean push (`--no-prune` opts out). Deleted: pack
files (`notebook-*`) superseded by the fresh pack, and session files whose
title exactly repeats a fresh upload (rerun dedup). Never touched: PDFs,
URLs, Drive, expert sources. Rationale: without prune, three identical root
packs accumulated in one day (2026-10-08) — same state, three citations.

## Promote rule (Q4 — an unpromoted answer is lost work)

Every actionable item in `answer.md` becomes exactly one of:

- `handoff/flags/<slug>.md` — when it says "do X"
- `DECISIONS.md` (D-next) — when it says "decide X" (ADR bar: hard to reverse +
  surprising + real trade-off)
- `SCARS.md` — when it says "watch out for X"

## Triggers (Q6 — on-demand only)

1. **On-demand before a strategic question.** A session that faces a debug or
   decision problem it cannot settle locally runs the pipeline, then asks.
   Scheduled runs are rejected (noise when nothing happens); threshold runs
   (after N new sessions) are deferred until N is defined.
2. **Closing-ritual hook.** `handoff/CONTEXT.md` carries the one-line version:
   strategic question ⇒ push first, then `nlm query notebook <id> '<q>'`.

## Anti-triggers

- Do not build a wrapper before `nlm doctor auth-replay` is green and one raw
  `nlm source add` lands `ready` (2026-10-07 scar: ~40 turns burned in reverse order).
- Do not repair anything under `notebooklm-py` (`~/.notebooklm-venv` is fallback only).
- `nlm login --check` is a local report, not a network test. `doctor auth-replay`
  is the only signal. `Authentication expired` with a green check = wrong default
  profile → `nlm login switch piwowarski`.
