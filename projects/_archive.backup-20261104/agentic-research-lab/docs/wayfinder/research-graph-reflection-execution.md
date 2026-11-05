---
type: Concept
title: research-graph-reflection-execution
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Wayfinder map: research ↔ knowledge-graph ↔ reflection ↔ execution

> **CONFIRMED 2026-10-01 — destination accepted by a human (option A).** The
> destination fixes the scope of the whole map, so charting preceded this
> decision; this line records the outcome, not a claim that the scope was
> obvious. Alternatives are listed in `## Destination alternatives` below —
> options B, C and D remain unexecuted and each states what it would *not*
> prove. Confirmation settled **what** this map is for. It did not settle any
> ticket: all five are still open, and T1 is the frontier.

## Destination

A single canonical execution seam joining the four layers, with the ambiguity
that currently blocks it resolved, and one gate proving the seam is load-bearing
rather than merely present.

Concretely, "reached" means all four of these are true and each is checkable by a
command, not by prose:

1. **One phase-04 runner is canonical.** `pipeline/06_reflect/spawn.py` (the
   `omp` agent loop) and `pipeline/06_reflect/reflect.py` (one LLM call over a
   presearched evidence packet) both claim phase 04 today. The map picks one,
   demotes the other to an explicit adapter or deletes it, and `CLAUDE.md`
   routes to the survivor.
2. **The execution layer's effect on agent behavior is measured.** Today
   `scripts/apply_meta_learning.py` rewrites `stages/*/CONTEXT.md` from promoted
   rules and is gated on no-regression (`quality_check.py`), which proves the
   rewrite did not break anything. Nothing measures whether the rewrite
   *changed* what an agent does. Either a measurement exists or the absence is
   recorded as a bounded decision.
3. **The layer seams each carry a gate that can fail on the seam**, not on a
   local property. This is the C-7 lesson in `CONTEXT.md`: 15 gates passed
   continuously through six defects because each asserted a *local* property
   while every failure was *relational*.
4. **A cold walk test passes** — a fresh agent answers "where am I / where do I
   go for task X" from the entry file plus at most two more reads, and can state
   pipeline status by scanning output folders alone (ICM walk test).

### Destination alternatives

| Option | Destination | Cost | Evidence it produces |
|---|---|---|---|
| **A (confirmed 2026-10-01)** | The above: canonical seam + measured execution + seam gates | ~4 sessions | A spec a second agent can implement without asking |
| B | Documentation only — contracts, data flow, gate placement, no new code | ~1 session | A design doc; explicitly does *not* prove the seam works |
| C | VERA research result: which of peer-review / external-grounding / eviction-predicate / ralph-fresh-context measurably improve grounding | ~3–6 sessions | A measurement, not a design |
| D | Working end-to-end run with gates on every seam | ~6+ sessions | A green pipeline run; risks freezing unchosen semantics into code |

Option A was confirmed on 2026-10-01 because B leaves the two-runner
ambiguity unresolved (which is the fact most undermining the integration), and
D writes code before the semantics behind it are agreed.

## Notes

**Domain.** This project's own corpus is the evidence base: the failure modes it
has already measured (`04_honest_lying_memory_confabulation`,
`02_expel_experiential_insight_extraction`,
`01_taxonomy_of_20_ai_research_failure_modes`) are the subject matter, and the
integration is not neutral with respect to them.

**Skills each session should consult.** `skills/icm-architect` for the walk test
and the ten invariants; `skills/ralph-loop` for one-frontier-node-per-iteration
discipline with a human confirmation boundary; `skills/unlazy` for gates
authored *before* implementation; `skills/grill-with-docs` for HITL tickets and
ADR capture; `skills/wayfinder` for the map itself.

**Standing preference — verification discipline.** Every claim in this repo's own
history that was later retracted came from one of three shapes: a metric
reported without printing what it scored (C-5), a gate whose docstring asserted
a property the code did not implement (`check_graph_determinism`), or a green
gate run against a different input than the one under discussion. A ticket is
not resolved by an agent asserting an outcome. The gate must run on the artifact
the change produced.

**Scope discipline.** This is a research lab, and the workspace rule is one
project per session with changes confined to it. The integration is *internal*
to `projects/research/agentic-research-lab`; sibling projects link, they are not
modified.

**Preflight.** `python preflight.py` before substantive work; exit 1 lists what
is missing.

## Decisions so far

<!-- one line per closed ticket: gist + link to the ticket that holds the detail -->

- **Reflection fast path: gates were written before implementation, and the
  backend question is still open.**
  ([`GATES-reflection-fastpath.md`](../../GATES-reflection-fastpath.md),
  [`reflection-fastpath.md`](reflection-fastpath.md)) — G1–G5 all met
  (256 tests green, artifacts grounded, `REFLECTION_FASTPATH_VERIFIED`), but the
  backend decision — pi model API vs. local endpoint vs. `omp` — was never
  closed, which is why `reflect.py` exists beside `spawn.py` rather than
  replacing it. This map inherits that unanswered question as ticket **T1**; it
  is not re-litigated from scratch.
- **Deterministic routing over model recall.** Established in
  [`pipeline/06_reflect/route.py`](../../pipeline/06_reflect/route.py) and
  enforced by `check_reflection.py`, which recomputes tag-intersection ordering
  and rejects a digest whose `returned_ids` differ. Same tags + same
  fingerprint ⇒ same id set. Carried forward as a constraint, not an open
  question.
- **Contracts must not hardcode moving values.** `check_stage_contracts.py`
  rejects a literal fingerprint in `stages/*/CONTEXT.md`. Verified live this
  session: `OK: checked 9 stage contracts — no hardcoded moving values.` The
  reason is structural — a contract quoting a stale fingerprint silently
  describes a graph that no longer exists.
- **Gate-first adoption is itself an unfinished map.** The root
  [`GATES.md`](../../GATES.md) holds a second, older wayfinder map
  (`integrate-unlazy-gate-first`) whose integration gates **N1** and **N2** are
  still unchecked, and whose **G1**–**G5** evidence lines are written but
  unverified against current outputs. This is a real collision — two
  `## Destination` bodies, one of them stale — and becomes ticket **T5**.

## Frontier tickets

Open, unblocked, takeable now. Claim before working. One ticket per session
except `research` tickets, which may run in parallel.

### T1 — Which runner is phase 04?
- **Type:** `prototype` (HITL) — the question is "what should phase 04 *be*",
  and a cheap concrete artifact settles it faster than argument.
- **Blocks:** T3, T4. Everything downstream inherits this choice.
- **Question:** Does phase 04 remain the `omp` agent loop (`spawn.py`), become
  the single-LLM-call path (`reflect.py`), or become a deterministic Python
  pipeline that calls a model only for the claim text?
- **Why it is sharp now:** both runners exist, both are referenced, and
  `CLAUDE.md` routes to the slower one while the faster one carries the
  metadata that satisfies `check_reflection.py`.
- **Prototype artifact:** a stub that runs `reflect.py` end to end on one topic
  writing to `reflection/scratch/`, plus measured wall-clock and token cost
  against the same topic via `spawn.py --scratch`. Both measured, neither
  trusted; the numbers are the input to the human's decision.
- **Resolved when:** one runner is canonical in `CLAUDE.md`, the other is
  either an adapter with a stated contract or removed, and the decision is
  captured as `docs/adr/0004-*.md`.

### T2 — Does rewriting a contract change agent behavior?
- **Type:** `research` (AFK) — answerable from this repo's own code without a
  human, so it may run in parallel with T1.
- **Question:** Can the effect of `apply_meta_learning.py` on
  `stages/*/CONTEXT.md` be measured, and if not, what is the minimum change
  that makes it measurable?
- **Why it matters:** the current gate proves *no regression*. Proving
  *positive effect* is a different claim. `CONTEXT.md` C-7 records that 6 of 8
  mapped defects had no gate at all, and that gates asserting local properties
  missed every relational failure — so this ticket must state which kind of
  property it measures, before it reports a number.
- **Resolved when:** a proposed measurement is written down with its oracle,
  its negative control, and an explicit statement of what it cannot detect.

### T3 — Gate placement on the four layer seams
- **Type:** `grilling` (HITL).
- **Blocked by:** T1 (path identity determines which seams exist) and T2 (the
  execution seam's gate depends on what T2 concludes is measurable).
- **Question:** For each seam — task→graph, graph→reflection, reflection→
  promotion, promotion→contract rewrite — what is the single observable that
  proves the seam works, and what is the negative control that proves the gate
  can fail?
- **Constraint carried in:** a gate that cannot fail on an ordinary mistake is
  decoration. Each gate ships with the mutation test that makes it go red.
- **Resolved when:** a `GATES-<slug>.md` exists with one runnable gate per
  seam, each with `CHECK:`/`EXPECT:` and a recorded negative control.

### T4 — Cold walk test of the integrated seam
- **Type:** `task` (AFK).
- **Blocked by:** T1, T3.
- **Question:** Can an agent with no session memory answer "where am I, where do
  I go for task X", state pipeline status by scanning output folders alone, and
  name the exact input path for each phase — in entry file plus ≤2 reads?
- **Resolved when:** a walk transcript exists with read counts, and every
  failure is fixed by moving or splitting a file rather than by adding
  explanation to a routing file.

### T5 — Reconcile the two live wayfinder maps
- **Type:** `task` (AFK).
- **Question:** What happens to the root `GATES.md` map
  (`integrate-unlazy-gate-first`) — is it resolved, superseded, or archived — and
  what happens to its unverified G1–G5 evidence lines?
- **Why it matters now:** a workspace with two `## Destination` bodies and one
  stale is a workspace where a cold agent cannot tell which plan it is
  following. This is the same defect class as the duplicated entry files
  `icm-architect` names as a canonical anti-pattern.
- **Resolved when:** exactly one map is live, and the other's fate is recorded
  rather than inferred.

## Not yet specified

Fog. In scope, but not yet sharp enough to ticket. Each patch graduates into
one or more tickets as the frontier advances, and is cleared from this section
when it does.

- **How far execution feedback travels.** If `apply_meta_learning.py` rewrites
  contracts, does anything observe the rewrite landing in an agent's *prompt*
  rather than only in the file on disk? Whether this is in scope depends on T2.
- **The relationship between the two memory systems.** `reflection/memory.md`
  (file, promoted rules, gated by `check_promotion.py`) and agentmemory
  (`:3111` service, consolidated by `close_session.py`) both claim to hold
  durable agent lessons. Which is authoritative for a given class of lesson, and
  what happens when they disagree, is unstated.
- **Whether `ralph-loop` is the execution mechanism for this integration at
  all.** `scripts/ralph_pilot.py` implements fresh-context-per-iteration with a
  cross-model reviewer, and deliberately overrides a deterministic gate to let
  the reviewer's verdict stop the loop. Whether that authority inversion is
  correct *for pipeline phases* (as opposed to for open-ended coding tasks) is
  unexamined, and it is the kind of question that is cheaper to decide before
  wiring than after.
- **`ralph_pilot.py` is currently broken and the break is unowned.**
  `tests/test_ralph_parity.py::GateIsAdvisoryTests` fails 2/2 with
  `AttributeError: 'A' object has no attribute 'same_model'` — line 292 reads
  `args.same_model` but no argparse definition registers it, and the file is
  modified-but-uncommitted (`git status`: ` M`). Observed during this charting
  pass, 2026-10-01. Deliberately not fixed here: it is outside the charting
  pass's `OWNS` scope, and ralph-loop's authority model is itself an open
  question above. Recorded rather than silently repaired, because a red suite
  that someone else introduced is a finding to hand over, not a gate to satisfy.
- **What "done" means for a research finding that produces no candidate.**
  `04_reflect` can legitimately end in `learned`, `wrong`, or `unresolved` per
  the `discuss.py` contract. Whether phase 04's gates treat "no rule emitted" as
  success, failure, or a third state is unstated — and `CLAUDE.md`'s own note
  that a pipeline which can only emit a rule pressures every session into
  manufacturing one suggests this is load-bearing.
- **Cost accounting across the seam.** `reflection/timings/` measures wall-clock
  per stage; `cost_ledger.py` exists; `ralph_pilot.py` prints a cost warning.
  Whether one number describes the whole task→reflection→evolve round trip is
  unstated.

## Out of scope

Beyond the destination. Never graduates; returns only if the destination is
redrawn, and then as a fresh effort rather than a resumption.

- **Changing corpus content, chunking, or the graph schema.** Measured dead
  ends are already recorded (`CONTEXT.md` C-4: chunk re-segmentation and four
  retriever levers all returned flat, with a negative control proving the metric
  was saturated). Re-litigating them spends budget for a known-zero result.
- **Removing `omp` as a runtime dependency.** T1 may demote `spawn.py`; the
  `omp` CLI itself is an environment concern, not a design one.
- **Sibling projects.** `knowledge-retrieval`, `benchmark-core`,
  `etth1-h720`, `research-engine`, `brain` are separate sessions. The
  integration may *link* to them; it does not modify them.
- **Retrieval ranking improvements.** `mean_family_recall` is 0.958 and
  `mean_concept_coverage` 0.958; the residual gap needs embeddings and is a
  `knowledge-retrieval` question, not this map's.
- **Deleting or rewriting historical reflection artifacts.** The workspace rule
  is that a gate-flagged artifact is evidence; stale output is quarantined, not
  removed.