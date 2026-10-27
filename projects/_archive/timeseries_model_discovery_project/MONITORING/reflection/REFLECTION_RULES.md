---
type: Concept
title: REFLECTION_RULES
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# REFLECTION_RULES.md — Deterministic Post-Work Reflection Protocol

> These rules are **deterministic**: every field, every trigger, every gate is checkable. There is no judgment call about whether a reflection is needed — the triggers below are exhaustive. A reflection is either complete (all gates pass) or incomplete (yield is blocked).

## R1. Scope & Trigger (when a reflection is REQUIRED)

Write a reflection file under `reflection/` at the close of any of these events:

| # | Trigger | Applies when |
|---|---------|--------------|
| T1 | **Task finished, no block** | A work item reached Yield with status `complete` |
| T2 | **Task yielded-partial or blocked** | Work ended `yielded-partial` or `blocked` |
| T3 | **Problem solved/analyzed** | A problem entry was created/updated in `MONITORING/KNOWLEDGE/problems/` |
| T4 | **User requested a reflection** | Human explicitly said "do a reflection" |
| T5 | **Contract/routing changed** | Any `.md` in `_factory/`, `ROOT/AGENTS.md`, or a `CONTEXT.md` was edited to alter rules or routing |
| T6 | **Problem lifecycle event** | A problem file in `MONITORING/KNOWLEDGE/problems/` reached `systematic_fix_applied`, OR an **open problem reoccurred** (recurrence), OR a user complaint was logged and recovered |

> Yielding with an incomplete reflection (T1–T5 pending) is a violation of the yield protocol (`_factory/OPERATOR_DOCTRINE.md` §7). BEFORE YIELD, the reflection MUST exist and pass all gates below.

## R2. File Naming (deterministic)

```
reflection/YYYY-MM-DD_HHMM_S-XX-slug.md
```
- `YYYY-MM-DD_HHMM` — local wall-clock time of the reflection (mirror `logs/` naming).
- `S-XX` — session identifier and slice/sequence (same scheme used in `logs/` and `problems/`).
- `slug` — 2–5 word kebab-case summary, e.g. `omp-extension-load-failure`.

## R3. Required Schema (fixed field order — machine-parseable)

Mirror `_template.md` exactly. Field name lines are `## ` headers or `- ` keys; do not reorder, rename, or drop fields.

| Field | Required content | Gate |
|-------|-----------------|------|
| `Title / Date / Status` | file title, date, status (`complete`\|`yielded-partial`\|`blocked`) | non-empty |
| `work_summary` | what work finished, in 1–3 sentences | non-empty |
| `problems` | one subsection **per problem**: `id`, `symptom`, `root_cause` | each non-empty |
| `solutions` | for each problem `id`: `solution`, `verification_evidence`, `files_changed` | `solution` + `verification_evidence` non-empty |
| `prevention_rules` | one rule (Invariant) per problem: `invariant`, `owning_doc`, `owning_doc_updated` (Y/N + commit/path) | `invariant` + `owning_doc` non-empty |
| `next_action_routing_changes` | routing/contract updates discovered and applied this session, or `none` | non-empty (`none` allowed) |
| `open_risks` | anything not verified / deferred / expected-but-empty | non-empty (`none` allowed) |

## R4. Gate Conditions (a reflection is complete only if ALL pass)

- **G1 — Schema:** every field above present and in order; exactly one `problems` / `solutions` / `prevention_rules` block.
- **G2 — No soft words:** `problem`, `solution`, `verification_evidence`, `invariant` must not contain banned qualifiers (`_factory/OPERATOR_DOCTRINE.md` §4): "should work", "probably fine", "looks good", "seems to", "I think", "generally", "more or less", "try to".
- **G3 — Evidence on every solved problem:** `verification_evidence` cites a log path, a re-runnable command, or a tool-produced artifact. A claim "fixed" with no evidence fails this gate.
- **G4 — Prevention rule routed:** every problem has an `invariant` and a concrete `owning_doc`. If the owning doc predates the rule, that's allowed (flag `owning_doc_updated: N`); if the owning doc does not yet cover it, `owning_doc_updated` MUST be `Y` and the doc updated in this session.
- **G5 — Routing applied:** any `next_action_routing_changes` item that names `ROOT/AGENTS.md` §2 or a `CONTEXT.md` was actually applied before completion. If a routing gap is discovered, `ROOT/AGENTS.md` §2 MUST reflect the new target this session.
- **G6 — Files listed:** every file the work created/modified is named (absolute or repo-relative) in `files_changed` or `work_summary`.

## R5. Where prevention rules go (deterministic routing)

| Problem class | Owning doc |
|---------------|------------|
| Global invariant / error protocol violation | `_factory/OPERATOR_DOCTRINE.md` |
| Monitoring/routing/reflection subsystem gap | `MONITORING/AGENTS.md` or `ROOT/AGENTS.md` §2 |
| Project- or workspace-specific gap | that project's `AGENTS.md` / `MONITORING/` |
| Process/stage contract gap | the relevant `PROCESS/<stage>/CONTEXT.md` |
| Cross-cutting diagnostic lesson | `MONITORING/KNOWLEDGE/problems/` + prevention rule in owning doc |

## R6. Deduplication

Before writing a new reflection, scan `reflection/` and `MONITORING/KNOWLEDGE/problems/` for the same `slug`/root cause:
- If the same problem class already has an invariant in its owning doc → do NOT create a duplicate prevention rule; reference the existing invariant (`owning_doc_updated: N`).
- If the same problem recurred despite an existing invariant → the invariant is insufficient; update it (and log the recurrence in `problems/`).

### R6b — Recurrence protocol (deterministic, 2026-09-04)

When capturing a new problem, run the recurrence lookup first
(PROBLEM_ROUTING.md §4): `python PROCESS/check_problems.py check "<fingerprint tokens>"`.
- **0 hits** → new problem file, `Recurrences: 0`.
- **≥1 hit, same surface** → a **recurrence**: reopen the existing problem
  file (`Status: open`), increment `Recurrences`, append a `## History`
  line. Do NOT create a new file (H4 blocks duplicate fingerprints at
  commit). A recurrence is ALWAYS a T6 reflection whose prevention rule
  MUST strengthen/replace the insufficient invariant in its owning doc —
  "solved for good" was premature, and the reflection says so explicitly.
- **≥1 hit, different surface** → new file; its `## Root Cause` MUST cite
  the prior problem ID and why the old invariant did not cover this surface.

## R7. Interaction with the session log

- The reflection is a **separate file** from `logs/session-*.md`.
- `session-*.md` records what happened (archive); `reflection/` records what was learned (rules).
- Write the reflection FIRST, then finalize the session log Touchdown, and reference the reflection path from the session log's summary if useful.

## R8. Example (resolved incident — local digest freshness)

> **Problem:** A corrupt brain-local skills digest passed the old overlay-based gate.
> **Root cause:** The verifier checked another artifact instead of the file consumed.
> **Solution:** Compare exact local digest bytes against the deterministic renderer.
> **Verification evidence:** Corrupt/missing local digest returned 1; restored bytes returned 0 (`PROCESS/05_verify/logs/2026-09-17_skills_relocation.json`).
> **Invariant:** Freshness checks MUST validate the authoritative artifact, including its missing and corrupt states, without repairing it during a check.
> **Owning doc:** `brains/CONTEXT.md` §3.

This is the normative reflection shape. Prior Windows hook-console and extension examples remain in historical reflection records.

## R9. Brain-Sync Closing Rule (deterministic, event-driven)

Any reflection whose work_summary names `INBOX/`, `brains/icm_brain/corpus/`,
or `brains/icm_brain/topics.md` (or whose `files_changed` list contains any
path under those roots) MUST close with the following verification sequence
executed **before the session yields**:

```bash
python build_brain.py && python brains/icm_brain/verify_sync.py
```

`verify_sync.py` MUST exit 0. A non-zero exit is a G7 gate failure: the
reflection is incomplete. The agent MUST run the full rebuild chain
(`python chunk_knowledge.py && python build_graph.py && python build_brain.py`)
until `verify_sync.py` reports `in_sync: true`, then re-run the closing
sequence above before yielding.

### Why
`icm_brain`'s SQLite knowledge graph (`rag.db`) and its `corpus/` files are
separately mutable. Without an explicit close-time rebuild, an agent may
yield with a stale `rag.db` even when the corpus was up-to-date earlier in
the session. The git pre-commit hook and the agent's PostToolUse hook
cover the editing window; R9 covers the **reflection-close window**, which
neither hook fires on.

### Enforcement contract

| Gate | Check | Failure mode |
|------|-------|--------------|
| G7a | Reflection's `work_summary` or `files_changed` references any of `INBOX/`, `brains/icm_brain/corpus/`, `brains/icm_brain/topics.md`. | Not a brain-touching session — R9 does not apply. |
| G7b | `python build_brain.py` exits 0 in the reflection's verification evidence. | Reflection incomplete; rebuild. |
| G7c | `python brains/icm_brain/verify_sync.py` exits 0 in the reflection's verification evidence. | Reflection incomplete; rebuild chain. |
| G7d | `verification_evidence` quotes the exact stdout of `verify_sync.py --json` (or `--quiet` confirmation). | Reflection incomplete; re-run. |

### Cross-reference
- Trigger paths: defined in `brains/icm_brain/HOOKS.md` §1.
- Sidecar schema: defined in `brains/icm_brain/verify_sync.py` module docstring.

### R9b — reflection_brain closing sequence (2026-09-04)

ANY schema-shaped reflection (`YYYY-MM-DD_HHMM_S-*.md`) changes the scar
corpus. Rebuild and verify the deterministic artifacts before yielding:

```bash
python brains/reflection_brain/build_reflection_index.py && python brains/reflection_brain/gen_digest.py
python brains/reflection_brain/verify_reflection_sync.py
```

Read `brains/reflection_brain/digest.md` explicitly. The verifier MUST
exit 0: it checks corpus/index integrity and exact local digest bytes.
Deleting a reflection also requires rebuilding; the unconditional
every-commit freshness gate catches deletion drift.

Optional Mnemopi recall may help retrieve knowledge; it is not a required
store, seeding step, or source of freshness authority. No native-Jcode
private-memory writes or reconciliation are part of this closing sequence.
