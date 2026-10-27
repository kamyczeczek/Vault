---
type: Concept
title: PROBLEM_ROUTING
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# PROCESS/PROBLEM_ROUTING.md — Problem Capture, Monitoring, Solve-For-Good, No-Circles

## 1. Purpose
This file establishes the mandatory, deterministic protocol for any problem,
bug, schema failure, wrong output, or **user complaint** encountered during
workflow execution. It guarantees two things, exactly as directed:
1. **Every problem is caught, monitored, and solved for good** — captured in
   `MONITORING/KNOWLEDGE/problems/`, carried as a visible open item until its
   systematic fix is verified, and flagged if it ever reappears.
2. **No going in circles** — before any plan or fix, the agent MUST query the
   accumulated problem+scar knowledge; a re-attempt of a previously failed
   approach is a routing violation.

Authority: `AGENTS.md` (Rules 4/5/6) → `WORKFLOW.md` (scenario playbooks) →
this file (problem lifecycle) → `REFLECTION_RULES.md` (T6 trigger, R10
gate). Integrity gate: `python PROCESS/check_problems.py` (commit-time).

## 2. Capture (what MUST become a problem file)
A problem file (`MONITORING/KNOWLEDGE/problems/YYYY-MM-DD_<slug>.md`,
copy `_template.md`) is required for:
- any error/exception/crash/test failure the agent hits (S3);
- any **user complaint** ("this is wrong", "that didn't work", "why did you
  X") — complaints are first-class problems, `Source: user_complaint`;
- any adjacent issue noticed while verifying another task's acceptance
  (the h720 S-03 pattern) — `Source: adjacent_issue`;
- any failure of a workspace gate (a gate blocking = a problem, not a bug
  in the gate unless the gate itself is proven wrong).

**Capture is immediate** — at the moment of encounter, before any fix is
attempted. The file starts `Status: open`, `Recurrences: 0`, and carries a
`Fingerprint` (3–8 surface tokens that uniquely identify the problem's
surface: files, components, concept — e.g. `pre-commit hook catalog drift`).

A problem that is not worth a file (typo, one-off env hiccup) MUST be
recorded as a one-line `## Minor` note in the session's reflection
`work_summary` instead — never silently dropped (Rule 4, No Silent
Failures).

### 2.1 Automatic detection (harness backstop — 2026-09-04)
Agent-encountered failures are ALSO captured automatically, independent of
agent discipline (`.jcode/hooks/failure_ledger.py`, wired via the Jcode
`post_tool` observer + transcript harvest + pre-commit gate):
- Tool errors (failed edit/write/read) land in the ledger at the moment
  they happen; shell failures (non-zero exits) are harvested from session
  transcripts at gate time. Full mechanism: `.jcode/hooks/README.md`.
- **The pre-commit hook blocks any commit while a ledger entry is
  undispositioned.** Disposition is the only judgment step:
  `dispose <id> problem <file>` (after filing per §2 above — same
  fingerprint rules apply) or `dispose <id> benign "<reason>"`.
- The failure ledger does NOT replace §2 capture. It is a net underneath
  it: anything the agent missed mid-session still blocks the commit.
  Benign dispositions are auditable (`.jcode/session-state/archive/`).

## 3. Solve-For-Good lifecycle (status machine)
```
open --(fix applied, verified)--> recovered --(systematic prevention in place)--> systematic_fix_applied
```
- **open** — logged, root cause unknown or fix not yet applied.
- **recovered** — the immediate failure is fixed and **verified** (a
  re-runnable command with its observed result in `## Verification`);
  the underlying class of failure may still exist.
- **systematic_fix_applied** — "solved for good": a prevention invariant
  exists, is routed to a concrete owning doc, and (where the workspace
  pattern allows) is machine-enforced (gate, hook, or verifier).
  **Only this status closes a problem.**

Rules:
- `open` problems MUST appear in `PROGRESS.md` under `## Open Problems`
  (one line each: `ID — one-line symptom — owning scenario`). No `open`
  problem may be invisible.
- A problem may not go from `open` straight to `systematic_fix_applied`
  without a `recovered` step AND a verification line (the H2 gate in
  `check_problems.py` enforces the shape; the sequence is doctrine).
- **User complaint:** recovery requires the user's acceptance signal
  (their reply, a re-run they can see) recorded in `## Verification`.

## 4. Recurrence (the "will not happen again" proof)
When a new problem is being captured, run the recurrence check first:
```
python PROCESS/check_problems.py check "<fingerprint tokens>"
```
- **0 hits** → new problem, `Recurrences: 0`.
- **≥1 hit, same surface** → this is a **recurrence** of an existing
  problem: do NOT create a new file. Reopen the existing file
  (`Status: open`), increment `Recurrences`, append a `## History` line
  with date + what re-triggered it, and write a reflection per
  `REFLECTION_RULES.md` R6: the existing invariant was **insufficient** —
  update the invariant in the owning doc (and record the update). A
  recurrence is always a T6 reflection (problem solved/analyzed) and the
  most important kind: it means "solved for good" was premature.
- **≥1 hit, different surface** → new file, but its `## Root Cause` MUST
  name the prior problem ID and state why the old invariant did not cover
  this surface.

## 5. No-Circles (consult before planning)
Before `03_plan` exits (stage contract, `03_plan/CONTEXT.md` Exit
Contract item 4), and before any S3 fix is attempted, the plan/fix MUST
carry a **Prior-Knowledge Check** section:
```
## Prior-Knowledge Check
- scars:  python brain/ask.py "reflection <task surface tokens>" --limit 3
- problems: python PROCESS/check_problems.py check "<task surface tokens>"
- failed approaches: PROGRESS.md "Failed Approaches" — none matching | <IDs>
```
Violations (a routing-level fail, not a suggestion):
- **Re-attempting a failed approach** listed in `PROGRESS.md` Failed
  Approaches without an explicit, recorded reason it might now succeed.
- **Planning a change** whose surface matches an `open` problem's
  fingerprint without the plan naming that problem ID (you may work
  around it; you may not ignore it).
- **Fixing a problem** whose recurrence check hit an existing invariant
  without citing that invariant in the fix.

This is what makes "knowledge from previous fights" load-bearing: the
scar brain supplies the invariants, the problems corpus supplies the
surfaces, Failed Approaches supplies the dead ends — and the plan gate
forces all three to be consulted and answered.

## 6. Close (per problem)
1. Status reached `systematic_fix_applied` with verification evidence.
2. Prevention invariant routed to the owning doc (the problem file's
   `Owning doc` field names it; `owning_doc_updated: Y` if the doc was
   changed this session).
3. The problem's lesson is reflected (T6) → the reflection's invariants
   flow through reflection_brain (R9b) into the scar channel — so future
   sessions auto-receive it.
4. `PROGRESS.md` Open Problems line removed (the problem file stays in
   `KNOWLEDGE/problems/` forever as corpus — it is the knowledge base).

## 7. Integrity gate — `PROCESS/check_problems.py`
Fail-loud, exit 1 on violation (runs at commit on trigger; see hook):
- **H1 shape:** every problem file (excluding `_template.md`) has a
  parseable `Status` in {open, recovered, systematic_fix_applied}, a
  `Fingerprint`, and (for recovered/systematic_fix_applied) a non-empty
  `Verification` section and `Owning doc`.
- **H2 terminal shape:** a `systematic_fix_applied` file must also carry a
  `Prevention Invariant` section and `Recurrences`.
- **H3 PROGRESS cross-check:** every `open` problem is listed in
  `PROGRESS.md` under `## Open Problems`; every `## Open Problems` line
  cites an existing problem file ID. (An open problem not in PROGRESS is
  invisible → blocked; a PROGRESS line pointing at a missing file →
  blocked.)
- **H4 fingerprint uniqueness:** two problem files may not share the same
  Fingerprint (the recurrence protocol says: reopen, don't duplicate).
- `check "<tokens>"` subcommand: print problem files whose Fingerprint
  shares ≥1 token with the query (the recurrence/no-circles lookup),
  exit 0 if any hit, 2 if none, 1 on usage error.

Trigger (pre-commit): `MONITORING/KNOWLEDGE/problems/`,
`PROCESS/check_problems.py`, `PROGRESS.md`. The cross-check (H3) is why
PROGRESS.md is in the trigger set — the two files must commit together.

## 8. Legacy files
Pre-v2 problem files keep their original shape and remain corpus (their
lessons are reflected and live in the scar channel). `check_problems.py`
accepts legacy status synonyms (`resolved`, `fixed`) as terminal for
pre-existing files only: any file dated 2026-09-04 or later MUST use the
v2 status set. New problems always use `_template.md`.
