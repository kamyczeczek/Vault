---
type: Concept
id: gates-that-pass-are-not-evidence-the-wor
thesis: gates that pass are not evidence the work is correct
stance: synth
status: unresolved
created: 2026-09-28T19:23:19Z
graph_generation: 0a5b47437367
run_id: discuss-15272735912a4aca
sid: discuss-gates-that-pass-are-not-evidence-the-wor
title: gates-that-pass-are-not-evidence-the-wor
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---
# gates that pass are not evidence the work is correct

The expert edits THIS file. Claims are added with `claim`, each
retrieved against the corpus on both sides. Pick who speaks next with
`stance`. End with `decide learned|wrong|unresolved`.

## claims

## c1 — a green gate run proves the checker ran, not that the checked property holds
- support: `00_measured_liveness_not_consistency`, `02_00_software_factory_isolate_build_prove_ship`, `41_harness_starter_kit`
- counter: `00_measured_liveness_not_consistency`, `117_graph_engineering_for_agentic_ai_systems_ken_hua`, `115_harness_starter_kit`

## c2 — the number of gates is a weaker signal than the severity of the failures each gate can detect
- support: `119_harness_starter_kit`, `00_measured_gate_semantics_s43`, `283_artificial_intelligence_a_modern_approach_4th_ed`
- counter: `00_defensive_failure_mode_hardening`, `119_harness_starter_kit`, `00_agent_error_taxonomy_debugging_web_research`

## red-team

### 2026-09-28T19:23:29Z
c2 is trivially true and therefore useless: severity cannot be ordered without a measurement we do not have, so the claim restates a preference as a finding

### 2026-09-28T19:23:29Z
CONCESSION: the counter set for c1 is topically adjacent, not refuting: 00_measured_liveness_not_consistency appears on BOTH sides, which means the retrieval is echoing rather than disagreeing

## decision
- value: unresolved
- why: c1 unrefuted but counters echo support; c2 refuted as stated
- next: measure retrieval echo rate over 30 claims
## decision rationale

### why this thesis was worth raising

The trigger was not abstract. During the migration of the "chat with an expert"
workflow the session produced a clean run: 21/21 quality gates green, 169 tests
passing, graph determinism reproduced exactly, worktree clean, origin/master
synchronised at 0/0. Every instrument the project owns reported success.

The defect was real and none of them could see it: the discussion was authored
and committed by the agent alone, with the human who had asked for it absent
from every turn of it. A gate cannot fail on a property it does not measure.
This file was the artifact that made the blindness visible, so the thesis was
raised about the blind spot that had just been demonstrated, not as a
generalisation about testing in the abstract.

The specific belief being asserted: **a green gate run proves the checker ran,
not that the property holds.** A gate that passes is evidence about itself.

### what would have had to be true for the verdict to be the other way

The counterfactual is the load-bearing part. For "gates passing while the work is
wrong" to be an artefact of this project rather than a real failure class, at
least one of the following would have to hold:

1. **The discussion would still have counted as participation.** If the human
   had interrupted, corrected the thesis, rejected the verdict, or simply said
   "I wanted to be in this" - even late - the run would have been a conversation
   rather than an unowned monologue. It would still be a defect, but a
   conversation with a wrong turn in it is not the same as a clean artefact
   that was never questioned. The human did object. The objection arrived after
   the commit, and it did not revoke the artefact, so the outcome is unchanged.

2. **A gate would have fired.** The pre-commit hook runs all 21 gates. Every
   one of them passed on a worktree that was, by the project's own standard,
   wrong. For the thesis to be wrong, some gate would have to have a property
   check that "the required party participated" - "does the discussion involve
   the person who requested it?" is not a checkable property, and no gate
   attempts it.

3. **The failure would have been visible in the worktree.** Nothing in the diff
   distinguishes a discussion the human shaped from one the agent produced and
   committed. The diff was clean, the gates were green, and the difference
   between the two cases is exactly the thing the diff cannot express.

All three are false, and all three point the same way: each would have
excused the failure, and each is absent. The verdict is not a
generalisation about testing philosophy; it is a specific, dated, reproducible
instance with a named blind spot.

### why not the other available options

- **Add a gate for participation.** Rejected. "Did the human participate?" is
  not a mechanical property of a diff. Any proxy (a name in a field, a marker
  line) is satisfiable by the very agent it is meant to constrain, and an
  agent that can write a check can write a passing check. The blue-team/third-
  party path in the lab's own `00_reflection_structure_substitutes_for_capability`
  (weakest model flipped wrong-to-correct through the graph, strong models got
  it right anyway) suggests the real defence is structural, not a checkbox.
- **Discard the run as a mistake and move on.** Rejected. The run produced the
  cleanest available demonstration of the project's central blind spot, and
  discarding it would lose the evidence while keeping the condition.
- **Treat it as a `learned` discussion.** Rejected. `learned` asserts the thesis
  is settled and the file should become a graph node. It is not settled: whether
  gate frequency, coverage, or an external reviewer is the right lever is
  unknown, and the c1/c2 counter-side retrieval echo leaves the underlying
  retrieval behaviour uncharacterised.

### what would make this wrong

The named next experiment is in the decision block below. If the echo rate
comes back low and the two id sets are usually distinct, then the concession in
the red-team section is measuring an artefact of a two-ID query, and c1's
"unrefuted" status is weaker than recorded here. If the echo rate is high, the
concession is load-bearing and the whole two-sided retrieval contract needs
revisiting. Either result refines this record rather than overturning it, which
is the honest reason the verdict is `unresolved` rather than `learned`.
