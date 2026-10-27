---
type: Concept
id: the-ralph-loop-fits-this-repo-s-mechanic
thesis: the Ralph loop fits this repo's mechanical gates and fails on judgement work
stance: red-teamer
status: learned
created: 2026-09-28T20:05:38Z
graph_generation: 0a5b47437367
run_id: discuss-804a0b9697134233
sid: discuss-the-ralph-loop-fits-this-repo-s-mechanic
title: the-ralph-loop-fits-this-repo-s-mechanic
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---
# the Ralph loop fits this repo's mechanical gates and fails on judgement work

The expert edits THIS file. Claims are added with `claim`, each
retrieved against the corpus on both sides. Pick who speaks next with
`stance`. End with `decide learned|wrong|unresolved`.

## claims

## c1 — a Ralph loop's exit condition must be deterministic, so it cannot judge work that has no deterministic acceptance criterion
- support: `67_graph_engineering_for_agentic_ai_systems_ken_hua`, `00_agent_hooks_lifecycle_guardrails`, `03_the_last_harness_you_ll_ever_build`
- counter: `01_new_markdown_file`, `01_taxonomy_of_20_ai_research_failure_modes`, `02_icm_ml_research_workflow`

## c2 — state that must survive a fresh session belongs in a bounded file, not in the derived graph
- support: `00_reflection_reorientation_cost`, `00_session_compaction_for_ai_agents`, `02_01_session_graph_research`
- counter: `00_reflection_reorientation_cost`, `00_session_compaction_for_ai_agents`, `02_01_session_graph_research`

## c3 — a second LLM model as reviewer is weaker than a deterministic gate as the loop's acceptance signal
- support: `02_agent_execution_hooks_guardrails`, `00_reflection_compaction_variance`, `00_measured_gate_semantics_s43`
- counter: `00_reflection_compaction_variance`, `00_32ecfce36290_graph_based_self_healing_tool_routi`, `02_agent_execution_hooks_guardrails`

## red-team



### 2026-09-28T20:06:10Z
c2 is refuted by its own retrieval, not by argument: support and counter returned byte-identical id sets, so the counter query never argued against the claim. Two-sided retrieval that returns the same set twice is topical echo, and the correct reading is 'not measured', not 'unrefuted'.

### 2026-09-28T20:06:19Z
c1 is weaker than stated: the graph supports the deterministic-exit requirement, but the counter set does not refute it either. The claim is not disproven so much as untested against this repo, because no Ralph loop has ever run here - the evidence is imported, not measured.

### 2026-09-28T20:06:19Z
c3's counter includes a graph-based self-healing tool-routing source, which is a real counterexample class: multi-model review is used precisely because a single deterministic check cannot cover judgement. If so, the two-model design is not decoration but a workaround for the same limit c1 describes.

### 2026-09-28T20:06:27Z
CONCESSION: the stated preference for a deterministic gate over a second model (c3) is not separable from the two-model design in the source video on the evidence retrieved; the counter id 00_32ecfce36290_graph_based_self_healing_tool_routi was not read, so the concession is narrower than it appears

## decision rationale

### why this thesis was raised

The trigger was a user-supplied video summary of Huntley's Ralph loop, asked
about as a possible primitive for this repo. That is a hypothesis imported from
outside, not an observation of this system - and the distinction turned out to
be the most important thing in this record.

The belief being asserted: a Ralph-style loop (fresh context per iteration,
state on disk) can carry this repo's mechanical work but cannot carry its
judgement work, because the loop's exit condition has to be deterministic and
judgement has no deterministic acceptance criterion. The practical consequence
would be a split: run loops over gates, never over verdicts.

### what would have had to be true for the verdict to be the other way

1. **That a deterministic stop condition is sufficient for this repo's work.**
   If the only thing an iteration needs to know is "did the gate go green",
   then a loop over the whole reflect stage would be safe, and the split is
   unnecessary. Not established - no loop has run here.
2. **That a second LLM reviewer can substitute for the deterministic gate.**
   The source video pairs a worker model with a reviewer model, and if that
   pairing is sound then "deterministic beats LLM" (c3) is wrong and the
   two-model design is the load-bearing part. The counter id
   `00_32ecfce36290_graph_based_self_healing_tool_routi` was retrieved and NOT
   read, so this remains genuinely open rather than refuted.
3. **That state in the derived graph would be safe across a rebuild.**
   The argument for a bounded file over the graph was partly that graph.db is
   regenerated and gated on determinism, so a handoff read from it could in
   principle differ from what the previous session saw. This was reasoned, not
   tested; and it is the weaker of the two reasons for preferring a file, since
   `00_reflection_reorientation_cost` already argues for bounded state on
   re-orientation grounds alone.

### why not the other available options

- **Adopt Ralph wholesale across the pipeline.** Rejected. The exit condition
  for judgement work is unavailable, and the failure mode when a loop cannot
  tell whether it converged is a plausible-looking repository that never gets
  there - not a crash. Nothing in the current gates detects that.
- **Add a semantic check that the handoff was understood.** Rejected. "Did the
  fresh session understand the state" is not mechanically checkable, and
  approximating it with a model reviewer reintroduces exactly the failure the
  same corpus documents: a checker that agrees with the agent's own account.
  What is checkable - did the iteration move the work forward - is the better
  target.
- **Build the reasoning-graph handoff first.** Deferred, not rejected. The
  reasoning graph is the one thing neither git history nor a progress file
  provides: why an approach already tried once was rejected. But it cannot be
  evaluated until a loop exists to hand off to, so the pilot comes first.
- **Close this as `learned`.** Rejected, and this is the load-bearing one. Two
  of three claims were not measured here; c2's counter set echoed its support
  set exactly. Recording the imported reasoning as settled would be the exact
  error this workflow exists to prevent.

### what would make this wrong

The named next experiment. If the scoped loop converges quickly and cheaply on
mechanical work, the split is confirmed and can be adopted. If it stalls -
if iterations stop producing gate movement, or if it re-proposes work a
recorded decision already rejected - then the failure is not "Ralph does not
fit" but "Ralph fits mechanical work and the reasoning graph is what makes it
safe", which would promote option 2 above from deferred to first.

The most likely way this record is wrong: c1 is supported by an imported
article about agent harnesses, not by anything measured in this repository.
If the first local loop contradicts the imported guidance, the imported
guidance was the weaker evidence and should be marked as such rather than
quietly dropped.

## decision
- value: learned
- why: c1, c2 and c3 are all settled, and not in the same direction. c1 MEASURED at b5e5083: a loop over check_dead_code.py converges in one iteration on injected defects, and honestly reports non-convergence when its worker cannot succeed. c3 REFUTED as a replacement for the deterministic gate, and read at last: graph-based self-healing routing cuts LLM calls 93% by routing deterministically and invoking the LLM only when no feasible path exists. It escalates; it does not substitute. c2 is REFUTED in principle by 00_reflection_compaction_variance: retained knowledge is variant across runs, not merely lossy, so a second LLM reviewer inherits the worker's hallucinated world and any token-overlap scorer is tuned against its own measurement. The abandoned branch showed exactly that - the blind negative control scored 0.50 until the scorer was hand-edited. c2 was therefore REPLACED rather than scored. What replaced it is a deterministic capability ladder (scripts/ralph_ladder.py, 4/4 rungs green) that measures commit attribution rather than understanding: a correctness gate is already green on iteration 0 and cannot tell a real iteration from a no-op, while a diff can, with no model in the loop. Rung 3 goes as far as a mechanical worker satisfying a written predicate - though note the ladder writes that predicate into check_dead_code.MANUAL and removes it again, so it measures obedience to a criterion it authored, not to a human's; rung 4, human judgement, stays out of scope by construction.
- next: Point the ladder at work that is NOT mechanical and see which rung fails first, now that the acceptance signal is a diff rather than a model. The open question is no longer whether a loop can be trusted but where its ceiling is: rung 3 assumes the criterion is externally authored, and the ladder has already shown that assumption breaking: it supplies its own predicate. The next measurement should find what happens when the criterion is externally authored and still under-specified.

## c3 override, 2026-09-29 - chosen knowingly, not discovered by accident

c3 above says a deterministic gate must be the acceptance authority and a
second LLM must not be. The Ralph implementation now does the opposite:
`scripts/ralph_pilot.py` reads `review-result.txt` and the reviewer's SHIP
stops the loop, while `check_dead_code.py` runs only as an advisory signal.
The gate is not the stop condition. This is visible in an end-to-end run:
the loop shipped with the gate still FAILing, because the reviewer said SHIP.

The user chose full parity with the upstream recipe after the divergence was
stated plainly, so this is a decision and not a drift. What it costs: for
mechanical work the gate is the better authority, and the override gives up
that advantage exactly where the gate was previously proven (see c1, measured
at b5e5083). What it buys: the loop can carry non-mechanical work the gate
cannot express a predicate for at all.

Consequence for the record: c3 is not refuted, it is overridden. The evidence
behind it is unchanged. Anyone reusing the deterministic-gate design for
mechanical work should read c3 as still standing; anyone running this loop
should read the override as standing.

- status: superseded by choice, 2026-09-29
- changed: scripts/ralph_pilot.py (reviewer authoritative), recipes/ralph-work.yaml,
  recipes/ralph-review.yaml (new), .goose/ ignored as generated phase state
- pinned by: tests/test_ralph_parity.py GateIsAdvisoryTests
- reference: https://goose-docs.ai/docs/tutorials/ralph-loop/
