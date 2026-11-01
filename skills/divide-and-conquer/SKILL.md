---
type: Concept
name: divide-and-conquer
description: "Split one task into independent workstreams and run each in its own sub-agent, in its own git worktree, on its own branch. Use when a task has 2+ pieces that write disjoint files and each piece can be verified on its own (e.g. separate modules + their tests, code vs docs, two independent scripts). Do NOT use for compute runs (benchmarks, fits, calibrations), for anything that writes a ledger / handoff flag / generated view, for edits to scripts/** hooks/** skills/** gates, or when one piece needs another's result."
title: SKILL
---

# Divide and Conquer (Vault edition)

Adapted from driangle/taskmd `divide-and-conquer` (lite plugin). Changes: no taskmd,
harness-agnostic, Vault rules (one project per session, single writer for flags and
ledgers, gates never loosened, shared CPU budget).

## 0. Gate — decide before spawning (30 seconds, write the answer down)

Spawn sub-agents only if **all** hold:

1. ≥2 workstreams, each with a **disjoint file set** (list the paths).
2. Each workstream has its **own verification** that does not need the others
   (e.g. `pytest <its test file> -q`).
3. No workstream writes: `ledger.jsonl`, `manifest.json`, `handoff/flags/**`,
   `HANDOFF.md`, `STATE.md`, `MAP.md`, `results/**`, or anything under
   `scripts/**`, `hooks/**`, `skills/**`, `check_workspace_integrity.py`, `audit_*.py`.
4. No workstream launches heavy compute (model fitting, benchmark, calibration).
   Sub-agents may run unit tests only. The 4-process CPU budget belongs to the
   orchestrator.
5. The harness has a sub-agent tool (Claude Code `Agent`/`Task`, opencode
   `task`/subagent with an available agent type such as `general` or `explore`).
   If it does not, do the work sequentially and say so.

If any condition fails, do the task directly. Write in the session's notes
which condition failed.

## 1. Prepare (orchestrator)

1. Read the project's `CLAUDE.md` → `CONTEXT.md`; run its `preflight.py`.
2. Base = current branch (`git rev-parse --abbrev-ref HEAD`), unless the user named
   another. Working tree must be clean (`git status --porcelain` empty).
3. Choose a flag name `<flag>` for this task (it is reused in the closing ritual).

## 2. Plan workstreams

For each workstream, write in a table **before spawning**:

| slug | files it may write | files it may read | verify command | depends on |

- Build a path→workstream map. Any shared path → those workstreams are
  **serialized**: the later one branches off the earlier one's finished branch.
- Disjoint ones form one parallel batch. Max **4** sub-agents per batch.
- A single workstream → no sub-agents, do it directly.

## 3. Create worktrees (orchestrator, not sub-agents)

Worktrees live **outside** the repo so the workspace integrity gate never sees them:

```bash
git worktree add ../Vault-wt/<flag>-<slug> -b dnc/<flag>/<slug> <base-or-predecessor-branch>
```

## 4. Spawn — one self-contained brief per sub-agent, all of a batch in one message

Each brief contains: goal, the exact write list and read list, the verify command,
the branch name and the worktree path, plus these rules verbatim:

- Work only inside `<worktree path>`. Never `cd` into or edit the main checkout.
- Write only the files on your write list. If you need another file, stop and report.
- Do not run model fits, benchmarks or calibrations. Run only `<verify command>`.
- Never edit a test or gate to make it pass. If one fails, report it.
- Do not write handoff flags, ledgers, `HANDOFF.md`, `STATE.md` or `MAP.md`.
- Before committing: `git diff --check` must print nothing. Then commit on your branch.
- Report: branch, final commit SHA, files changed, the verify command output (pass/fail),
  and anything you could not do.

## 5. Collect

- Wait for the whole batch. For each report, check: SHA exists, `git diff --name-only
  <base>..<branch>` ⊆ its write list, and re-run its verify command yourself.
- A failure is fixed by the orchestrator on that branch, not by re-spawning blindly.
  After two failed attempts at the same thing → query session memory
  (`scripts/memory/CONTEXT.md`) before trying again.

## 6. Finish — ask, don't auto-merge

1. Show the user: workstream, branch, SHA, verify status, any write-list violations.
2. **Ask** whether to integrate. Only on a yes:
   - merge each branch into base (`--no-ff`), run the project's full test suite and
     `python scripts/check_workspace_integrity.py`;
   - `git diff --check` clean, then commit.
3. Remove the worktrees and branches that were merged:
   `git worktree remove ../Vault-wt/<flag>-<slug>` and `git branch -d dnc/<flag>/<slug>`.
   Leftover worktrees count as drift.
4. Closing ritual (orchestrator only): write `handoff/flags/<flag>.md` listing which
   workstreams ran in parallel vs serialized and their SHAs, then
   `python scripts/build_handoff.py` and `python scripts/build_state.py`.

## Fit in current work (example)

Benchmark v2, Phase 1: `manifest.py`, `metrics.py`, `bootstrap.py`, `ledger.py`,
`guards.py`. Each comes with its own test file, so they can run as one parallel batch
of 4 plus 1 serialized. Shared fixtures (`conftest.py`) are written by the orchestrator
**first**, before the batch. Phase 1b dry run and every cycle run stay with the
orchestrator.

## Pairs with

- `unlazy` — a substantial workstream gets its own gates file (solo mode); the
  orchestrator re-runs each returned leaf's gates instead of trusting the report.
- `token-hygiene` — sub-agent briefs are read once; keep them tight and cap their
  output, because every line is re-paid context.
