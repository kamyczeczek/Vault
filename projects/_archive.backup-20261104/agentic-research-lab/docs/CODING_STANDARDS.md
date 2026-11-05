---
type: Concept
title: CODING_STANDARDS
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# Coding standards — loaded by the reviewer/verifier, not the implementer

These are the rules a **reviewer** applies when judging a change. They live
here rather than in `CLAUDE.md` because that file is loaded by every agent
doing every job, and a checklist nobody can act on is worse than no checklist.
The reviewer is the one role that must not wave a diff through, so the
standards are loaded only there.

`CLAUDE.md` keeps the two-line summary and points here. Nothing is duplicated.

## Evidence integrity (the rule that has already cost a run)

1. **A gate-flagged artifact is evidence.** `FAIL:` output is the measurement.
   Fix the cause, or mark the run `failed` and leave the artifacts on disk.
2. **Never delete an artifact because its contents are unflattering.** Check
   `reflection/.snapshots/` first — the graded copy already exists.
3. **Never re-run a gate against a different input and report that result.**
   If the artifact moved, you graded something other than the change.
4. **PASS is not VERIFIED.** PASS = gates green. VERIFIED = gates green on the
   artifact *this change produced*, after it ran. Use
   `python scripts/check_reflection.py --paths <topic-slug>`.

## Review procedure

- Run the gate on the changed scope, not the whole tree. A directory-wide
  gate cannot distinguish "my change is broken" from "an old artifact is
  broken", and the first reading of the difference is always the reassuring one.
- When a gate fails on a change you are reviewing, that is the review finding.
  Do not repair it by changing what is graded.
- **Default when a gate fails: mark the run `failed` and fix the cause
  upstream (prompt, worker, deterministic step) — never hand-edit the graded
  artifact.** A reviewer editing the artifact it reviews is the same authority
  that produced the false PASS: one role, two powers. Mechanical provenance
  backfill is deterministic and already handled by `attach_trace_provenance`;
  there is no legitimate case for hand-editing a graded file.
- Report the command you ran and its output. A finding without a command is a
  hypothesis.
- If the review is ambiguous, say which reading you took and why. Do not
  resolve ambiguity by picking the reading that permits a pass.

## Python conventions

- Explicit typing on function signatures; strict null handling.
- One job per function. Split rather than branch.
- Grep before inventing a pattern; a second idiom for an existing one is a
  defect even when it works.
- No untyped signatures, no unhandled broad `except` in code that makes
  decisions, no new dependency without a reason recorded in the commit.
- Windows: no inline `python -c` / `powershell -Command` with nested quotes or
  paths — MSYS mangles them. Write a temp file and execute it.

## Token economy (context hygiene)

- Targeted reads over whole-file dumps: symbol search or line slices for files
  over ~200 lines.
- Filter command output; inspect the failing assertion, not the whole log.
- Plan before a multi-step task; outline before modifying.

## Retro inputs

When a review finds a defect that a check *could* have caught, the deliverable
is the check, not the fix alone. Add it to `scripts/check_*.py` and to
`scripts/check_evidence_guard.py` where it concerns evidence integrity, so the
next occurrence of the same shape is caught by a script rather than by a
reviewer noticing.

## Model routing

The incident's lesson is not just deterministic gates — it is also that the
model tier must match the task shape. A fast-tier model under a metric it
controls will optimize the metric, not the goal. The fix is routing, not a
stronger prompt.

| Task | Tier | Reason |
|---|---|---|
| Single-file edit, grep, format | fast | small blast radius |
| Multi-file refactor | strong | cross-file invariants |
| Verification / gating | strong | optimises truth, not a metric |
| Write or delete on graded artifacts | strong, or separate process | reward-hack surface |

This workspace has no router config surface, so routing is a conscious
choice made at the start of each task, not a default. The question to ask:
"Does this task require resisting a gate failure?" If yes, it needs a strong
model or a deterministic check that the fast model cannot bypass.
