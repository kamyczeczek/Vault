---
type: Concept
title: 2026-09-15_contracts-hardcoded-moving-values
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# Reflection — contracts hardcoded moving values; a dead tag routed to nothing

Date: 2026-09-15
Project: projects/workspace-research
Trigger: T1 (problems were hit and fixed), T2 (a rule was added), T3 (a gate was retro-fitted)

## Problem

Two defects, both of the same family: a value that moves was pinned in prose, so the
documentation described a state that no longer existed, and nothing checked it.

1. **Three of four stage contracts hardcoded a corpus fingerprint that had moved.**
   `stages/03_graph/CONTEXT.md` still cited `1cf1e4aea87c` — the fingerprint *before*
   the 2026-09-15 corpus tag repair — while the live value was `0626262b2982`.
   `stages/01_inbox`, `02_corpus`, and `04_reflect` hardcoded the then-current
   `0626262b2982`, correct the day they were written and wrong the day after any
   corpus edit. The contracts are the Inputs Table agents read as their routing
   surface, so a stale one silently points at a graph that does not exist.

2. **A routing tag absent from the vocabulary matched zero chunks, silently.**
   `pipeline/06_reflect/_audit_workspace.prompt` mandated
   `ask.py --tag icm --tag agent-workspaces` as its *first* principle query.
   `agent-workspaces` is not in `knowledge/topics.md` and no chunk carries it, so that
   query returned nothing and printed no warning. For two sessions the audit's opening
   routing step was a no-op that looked like a successful empty result.

A third, related break surfaced while fixing these: a corpus chunk
(`icm-determinism-rule.md`, written by the concurrent audit pass) declared a composite
`source:` string naming five contributor chunks. The derived manifest gained a 36th row
for it, but `knowledge/raw/manifest.jsonl` on disk still held 35, so the phase-1/2 gate
correctly reported `untraced corpus (manifest has no row)`.

## Root cause

The values are live; the documents are static; nothing connected them. A fingerprint is
recomputed on every corpus edit and a plan version on every `WORKFLOW.md` edit, but the
contract prose quoted them as constants. This is the same defect class the project had
already fought in reflection outputs (three digests carried a pre-repair fingerprint,
caught only by the P5 gate) — it had simply not been checked in the *contracts that
describe the gate*.

The dead tag is the read-side twin: `ask.py` treated "matched nothing" as an ordinary
empty answer and returned exit 0, so a typo or a renamed vocabulary term was
indistinguishable from a legitimate no-result. An unenforced contract and an silent
empty result are the same failure — a system that reports success when it did nothing.

## Solution

1. **`scripts/check_stage_contracts.py`** (new) — a `stages/*/CONTEXT.md` may quote the
   current fingerprint only *beside* a pointer to `knowledge/graph/.graph_fingerprint`,
   the live source. A bare 12-hex literal with no pointer is a violation (exit 1).
   The value may appear; the caveat must appear with it. The gate is wired into
   `pipeline/WORKFLOW.md` (P7) and enforced at `spawn.py` entry, which now refuses with
   `STAGE_CONTRACT_STALE` instead of spawning an agent against a lying Inputs Table.
2. **All four stage contracts de-hardcoded** — fingerprint read live, with the current
   value kept inline for a human reader and named as time-of-writing.
3. **`_audit_workspace.prompt`** — `agent-workspaces` → `interpretable-context`
   (12 chunks, the ICM core). Verified: the dead query returned zero chunks, the
   replacement returns the intended principle set.
4. **`ask.py` now fails loud on an empty `--tag` intersection** (exit 2, naming the
   offending tag and pointing at `topics.md`). The extension's programmatic caller is
   wrapped in try/catch and prints the error, so it degrades to a message, not a crash.
   A non-empty `--tag` that matches nothing is a routing error, not an answer.
5. **Manifest regenerated**: 36 rows / 597 corpus ids, now tracing the derived-rule
   chunk's composite source. Graph and corpus reconciled at 597 nodes both ways
   (symmetric difference empty).

## Verification

Negative controls, both gates:
- `check_stage_contracts.py` on a bare literal `fingerprint 35b86bc954fa unchanged`
  ⇒ flagged; on an annotated `read knowledge/graph/.graph_fingerprint (currently
  0626262b2982)` ⇒ allowed; on a literal 400 chars from any pointer ⇒ flagged;
  on a 24-hex sha and a 6-hex fragment ⇒ ignored (no false positives).
- `ask.py --tag icm --tag agent-workspaces` ⇒ exit 2 with the dead-tag message;
  `--tag icm --tag interpretable-context` ⇒ exit 0 with chunks; a free-text query ⇒
  exit 0.

Full suite green:
- `check_stage_contracts.py` — OK, 4 contracts, no hardcoded moving values
- `check_manifest.py` — PASS, 36 rows / 597 chunks / 0 unmapped / 0 no-source
- `watch.py --once` — graph fresh, `nodes == corpus` (597 both ways)
- `check_reflection.py` — OK, 8 digests / 8 candidate files, all grounded
- 16 reflection outputs re-stamped to `fingerprint 17a3297a22fc`,
  `plan_version a2d5b26552ee` (both values confirmed stable across repeated reads
  before stamping).

Root `PROCESS/run_gates.py --all`: 12/12 pass.

## Prevention rules

- **R1 — a contract that quotes a moving value must point at where the value lives.**
  The fingerprint and the plan hash change on every edit; quoting them as constants
  makes the contract a lie on the day after the edit. The value may appear for a human
  reader, but only beside the live source. `check_stage_contracts.py` enforces this at
  gate time, not at audit time.
- **R2 — an empty routing result is an error, not an answer.** A `--tag` intersection
  that matches nothing means the vocabulary moved or the query was misspelled. Exit 0
  on empty let a dead tag sit in an audit prompt's first routing step for two sessions,
  looking exactly like a legitimate no-result. Distinguish "no match" (routing bug)
  from "few matches" (information).
- **R3 — the gate must check the artifact, not a reconstruction of it.** The manifest
  break was found only by comparing the on-disk 35-row manifest against a freshly
  derived 36-row one. Verifying a derivation against itself is a no-op gate — the same
  R1 the prior record established, holding here a second time.
- **R4 — stamp last, and only once both moving values are stable.** Re-stamping while
  still editing `WORKFLOW.md` or ingesting corpus moves the fingerprint and the plan
  hash under the stamp, producing output that is stale the moment it is written. Confirm
  both values across repeated reads before any stamp.
