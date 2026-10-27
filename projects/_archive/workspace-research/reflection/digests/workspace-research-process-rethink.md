---
type: Concept
title: workspace-research-process-rethink
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

fingerprint: 5f4f9d29057b  plan_version: ad0a031aa564  phase: 04_reflect  routing: manifest research_process(--tag reflection); manifest planning_horizon(--tag planning --tag reflection); manifest task_division(--tag planning --tag decomposition); manifest reflection_process(--tag reflection --tag context-engineering); manifest problem_monitoring(--tag agents --tag reflection); manifest knowledge_storing(--tag memory --tag retrieval); manifest graph_building(--tag knowledge-graph --tag determinism); manifest unified_brain_routing(--tag knowledge-graph --tag retrieval); expansions: ask.py "planning horizon" --limit 8, ask.py "task decomposition" --limit 8, ask.py "frontier state negative result" --limit 6, ask.py "confabulation memory lying" --limit 6, ask.py "provenance fingerprint determinism" --limit 6, ask.py "frontier state" --limit 6; route.py --tag planning --tag world-models --limit 12 --json; route.py --tag planning --tag decomposition --limit 12 --json

# Reflection: workspace-research-process-rethink

Rethinking this project's own working process — research, planning, task division, reflection,
problem monitoring, knowledge storage/retrieval, graph building, and the unified-brain goal —
as a phase-04 reflection grounded in the routed chunk ids. Distinguishing what is already built
from what is missing is the point of this digest: seven of the eight focus areas have a
shipped mechanism, and in every one of those seven the shipped mechanism is *conditional* —
it works inside its own boundary and has a named, unmonitored boundary condition.

---

## Area 1 — Effective research process

### Claim
The research loop is real and closed at the artifact level (INBOX → corpus → graph → reflection →
eviction), but its *intake* end is vocabulary-shaped, not question-shaped. `route.py` returns the
same `reflection`-tagged set for a process question and for a paper question, and the FTS5 leg
returns nothing for a 3-term question (verified twice this session: `speculation horizon reality`
and `verification negative control` both returned zero chunks). This is correct AND-semantics, but
it means the corpus's own concepts are only reachable if the questioner already knows the corpus's
vocabulary.

### Evidence
- `00_interpretable_context_methodology_folder_structu` — ICM replaces framework orchestration with
  filesystem structure; numbered folders as stages, markdown as interface. The project's
  `01_inbox..05_evict` stages are exactly this. **Already built.**
- `00_icm_43_copies_four_moves` — the cold-walk test: a fresh agent opening only the start file must
  route to one real job unaided. This project's equivalent is `ask.py --tag`, and it works — but the
  *entry* condition (knowing the tag) is undocumented in the working agent's context.
- `00_reflection_closed_vocabulary_before_content` — "the vocabulary must be maintained, or
  questions silently go unanswered." This is the boundary condition named in the corpus itself and
  it is currently unmonitored: `check_reflection.py`'s `dead_route_tags()` checks that *prompt*
  tags exist in `knowledge/topics.md`, but nothing checks that a *question* a working agent would
  ask can actually reach an answer.
- `00_is_progressive_disclosure_all_you_need_for_long` — "A second, deeper routing level never
  helped and sometimes breaks accuracy outright, so one level is enough." Constrains any fix to
  flat alias registration, not a router-of-routers.
- `00_awesome_context_engineering` — the field's taxonomy of the decay mechanism: context
  retrieval/processing/management/compression/isolation as distinct concerns, plus "Context Rot:
  How Increasing Input Tokens Impacts LLM Performance" and `context-pruning` /
  `context-distraction` / `context-poisoning` as named failure modes. A far-horizon plan is a
  larger input payload that accumulates exactly these failure modes — the mechanism behind the
  context-window-pressure finding in Area 2.
- `00_reflection_retrieval_dominates_write` — retrieval method moved accuracy 14–23 points vs
  write strategy's 3–8; precision predicted accuracy at r = 0.98. **The research process should
  spend its next unit of effort on retrieval reachability, not on better chunk writing.**

### Decision
Keep the 5-phase pipeline; do not add a phase. Add a **vocabulary-reachability check** as a new
phase-4 sub-gate: for a fixed list of *questions* the working agent is expected to ask, assert each
reaches ≥1 chunk via either tag intersection or FTS. Zero-hit questions are reported, not silently
accepted. This is the smallest edit that converts the corpus's own named boundary condition
(`00_reflection_closed_vocabulary_before_content`'s "silently go unanswered") into a gate.

### Next bet
Add `scripts/check_reachability.py` seeded with ~10 questions drawn from this session's own zero-hit
runs (`speculation horizon reality`, `verification negative control`, `idea inbox capture`) plus
known-good controls; exit 1 if any seeded question reaches zero chunks. Falsifiable: if the seeded
questions all hit after a topics.md alias addition, the check passes; if a question remains
unreachable, the vocabulary gap is real and named.

---

## Area 2 — Planning horizon (headline)

### Claim
**The next step must be based on reality the most; a plan with a bigger horizon is based more on
speculation.** This is not a general platitude about planning — it is the specific asymmetry this
corpus measures. Every long-horizon plan in the literature is a *speculative* artifact: the planner
commits to phases 3–5 before the evidence from phase 1 exists, and the corpus's own measurements
show both that the far phases are the least reliable and that the near phase is the only one with
real evidence behind it. Three measurements pin the asymmetry:

1. **A subpar plan hurts more than no plan at all.** `00_from_plan_to_action_how_well_do_agents_follow_th`
   (21,120 trajectories, 4 LLMs, 8 plan variations): an explicit plan improves resolution, but a
   *wrong* plan is worse than removing the plan entirely. A long horizon multiplies the surface
   where "wrong" can live.
2. **The far end of the plan decays first.** The same study's context-window-pressure finding: as
   trajectories grow, the initial plan "must compete with an increasingly long history," so
   deviation is *structural*, not incidental — the plan's influence decays with distance from when
   it was written. Distance in a plan is exactly horizon.
3. **A plan that is mostly speculation has no grounding channel.** `00_06_self_correction_grounding_requirement`
   — intrinsic self-correction *degrades* performance because judgement is the same capability
   applied to its own output. A far-horizon plan can only be validated by the planner's own
   anticipation, which is precisely the unverified critique this paper shows actively moves the
   model away from a better answer. The near step, by contrast, is validated by the environment.

So the correct structure is a **monotone evidence gradient**: step 1 is validated by the
environment, step 2 by a gate over step 1's artifacts, step 3+ by anticipation only. The
project's `WORKFLOW.md` already implements this gradient in *form* — each phase's entry condition
is the previous phase's exit gate — but it does not implement it in *substance*, because phases
3–5 are specified with the same confidence and the same detail as phase 1. Detail is the tell:
the amount of plan detail should be inversely proportional to the distance from the current
reality, because detail is what a speculation claims to have.

The same gradient is independently visible in the project's own measured lessons:
`00_measured_closed_families_need_frontier_state` — "the next proposal can re-enter a closed family
because nothing machine-visible says it is closed," and `00_measured_pre_registered_gate_s44` —
"the decision must be designed before the evidence exists." Both are the same insight at a
different grain: a distant decision made on not-yet-existing evidence is not a plan, it is a
pre-commitment that will be rationalized later.

### Evidence
- `00_from_plan_to_action_how_well_do_agents_follow_th` — "A subpar plan hurts performance even
  more than no plan at all"; "Without an explicit plan, agents fall back on internalized
  workflows... often incomplete, overfit, or inconsistently applied"; context-window pressure
  finding (§4.1.1). **Already built (partially):** `pipeline/WORKFLOW.md` exists as the canonical
  ordered plan this study says is required.
- `09_from_plan_to_action_how_well_do_agents_follow_th` — "periodic plan reminders improve plan
  compliance... consistent improvements in success rates across models... prevent drifting into
  irrelevant sub-goals." **Already built:** `stages/04_reflect/CONTEXT.md` P3 re-anchors on
  compaction/every N calls.
- `03_from_plan_to_action_how_well_do_agents_follow_th` — plan compliance metrics PPC/POC/PPF and
  Finding 11: "Agents prioritize effective workflows over prescribed phase ordering." A plan that
  over-specifies far steps *causes* the POC violations this metric measures.
- `00_06_self_correction_grounding_requirement` — intrinsic self-correction degrades; "a
  correction loop with no external grounding actively moves the model away from its initial
  (better) answer."
- `00_measured_closed_families_need_frontier_state` — "Recording a verdict records that a thing
  was tried. Recording the frontier state is what makes the next proposal different from the last
  one." The frontier state is the *reality* the next step must be based on.
- `00_measured_pre_registered_gate_s44` — "A pre-registration over evidence that does not exist
  yet is not a pre-registration; it is a plan to tune until it passes."
- `00_plan_persistence_context_window_compaction` — durable plans as external state; "Freeform
  summaries drop the dead-end record and invite loops retrying failed approaches."
- `00_adapt_as_needed_decomposition_and_planning_with` — ADAPT: decompose *as needed*, when the
  executor signals inability (+28–33% over static plan-and-execute). The empirical case that far
  decomposition should not be pre-committed.
- `234_icm_knowledge_big` — the priority key that operationalizes the same gradient in practice:
  "P1 — This week or deadline-critical / P2 — Important, 2–4 week horizon / P3 — Backlog / someday."
  Horizon *is* the priority axis here; P3 is explicitly *speculative* and is given no detail.
- `00_improving_planning_with_large_language` — MAP decomposes planning into recurrent specialized
  modules (conflict monitoring, state prediction, state evaluation, task decomposition,
  orchestration) precisely because a monolithic long-horizon plan hallucinates transitions and
  falls into loops.
- `00_enhancing_llm_based_agents_via_global` — GoalAct's "continuously updated global planning":
  the global goal is kept *continuously updated* rather than committed once, which is the
  alternative to a speculative frozen far-horizon.

### Decision
Keep `pipeline/WORKFLOW.md` as the single ordered plan. **Add an explicit horizon grading to it:**
each phase row gains a `basis` column classifying its specification as `environment-validated`
(phase 1, whose entry is INBOX state), `artifact-validated` (phases 2–4, whose entries are prior
exit gates), or `anticipation-only` (phase 5 and any forward-looking section). Detail density must
follow the gradient: phase 1 gets a full procedure, phase 5 gets a gate contract and a frontier
pointer, not a procedure. Concretely, this digest's own `Next bet` sections are written one step
deep — the smallest falsifiable step — rather than as a roadmap, and that is the pattern to
promote into `WORKFLOW.md`.

### Next bet
Add a `basis:` column to the five phase rows of `pipeline/WORKFLOW.md` and a one-sentence rule
under Compliance: "specification detail is inversely proportional to horizon; a step beyond the
next gateable artifact is stated as a bet, not a procedure." Falsifiable: a subsequent reflection
can cite the column and show a far phase that carries procedure-level detail — that citation is
the violation, and it is now detectable.

---

## Area 3 — Task division

### Claim
Task division in this project is already HTN-shaped and already adaptive — but the adaptivity is
implemented in one place (`route.py`'s threshold split) and the corpus's own task-division
literature says the split trigger must be the *executor's observed inability*, not a cardinality
threshold. `route.py` splits when `card < threshold`; ADAPT splits when the executor fails.
Cardinality is a proxy, and the proxy is wrong in the specific case that matters: a route that
returns many chunks that are all *the wrong* chunks never triggers a split.

### Evidence
- `ai-planning-htn-pddl` — the classical substrate, and the project's own mapping: "topic ->
  topic__coTag leaves = HTN decomposition with SHARES_TAG methods; task_plan.md phases are task
  network." **Already built:** the graph's decomposition is HTN with explicit methods.
- `00_adapt_as_needed_decomposition_and_planning_with` — "recursively decomposes sub-tasks to adapt
  to both task complexity and LLM capability"; decompose "when the LLM is unable to execute them."
- `04_modular_task_decomposition_anddynamiccollaborati`,
  `00_modular_task_decomposition_anddynamiccollaborati` — modular decomposition driven by LLMs,
  with a *sensitivity analysis on the number of decomposition modules*, i.e. the count is itself
  the experimental variable, not a fixed threshold.
- `00_interpretable_context_methodology_folder_structu` — one agent reading the right files at the
  right moment replaces a multi-agent framework; sub-agents inherit scope from the same tree.
  **Already built:** `spawn_recursive.py` leaves inherit scope by topic tag.
- `00_improving_planning_with_large_language` — MAP's task-decomposition module as one of five
  recurrent specialized modules: decomposition is a *capability*, not a pre-processing step.
- `00_chief_of_staff_routing` — routing as classification with a real cost model: "misrouting
  costs more than not routing, and the classifier needs visibility into downstream capabilities."
  The cardinality proxy has no visibility into downstream capability at all.

### Decision
Keep the HTN one-level split. **Change the split trigger from cardinality to a failure signal:**
record, per routed leaf, whether the consuming agent produced a digest whose claims all resolved.
A leaf with a high zero-resolution rate is the ADAPT inability signal; the next route into that
topic splits one level regardless of cardinality. One level only, per
`00_is_progressive_disclosure_all_you_need_for_long`.

### Next bet
Extend `route.py --json` output with a `split_signal` field that reads the last digest's
citation-resolution result for the topic, and split when that signal is failure rather than when
`card < threshold`. Falsifiable: run the same topic before and after — if the id set changes only
when the prior digest failed, the trigger is failure-driven; if it changes on cardinality alone,
the proxy is unchanged and the bet failed.

---

## Area 4 — Reflection process

### Claim
The reflection process has the two mechanisms the corpus says are non-negotiable — an external
grounding channel (citations must resolve in `graph.db`) and an eviction mechanism (phase 5) —
and it is still missing the third: the reflection is not *constrained in what it may diagnose*.
`04_honest_lying_memory_confabulation`'s mitigation is not "add a gate," it is "replace open-ended
self-diagnosis with programmatic extraction of trajectory-level failure signals... The
environment, not the agent's own reasoning, supplies the error content" (correct-object mention
0% → 86%, RRR 0.64 → 0.10). This project's reflection prompts ask for a diagnosis; the corpus says
the diagnosis must be extracted from artifacts, not composed.

### Evidence
- `04_honest_lying_memory_confabulation` — 0 of 121 reflections mentioned the correct target
  object; confabulated reflections were *reused across trials*. The mitigation: constrain the
  diagnosis. Solves 3/16 — "grounding is necessary but not sufficient."
- `00_06_self_correction_grounding_requirement` — "a model that cannot reliably solve a problem
  also cannot reliably judge whether its solution is correct." Reflection without an external
  channel is this failure mode.
- `00_08_lesson_persistence_eviction_requirement` — ExpeL's ADD/EDIT/UPVOTE/DOWNVOTE ledger with
  eviction at importance zero; "even successful trajectories can be suboptimal and mislead the
  generated insights." **Already built:** phase 5 `05_evict` implements exactly this.
- `02_expel_experiential_insight_extraction` — insights come from *contrasts*: a failed trajectory
  vs a successful one on the same task. The project's candidates have no contrast source — there
  is no failed-run record to contrast against a successful one.
- `01_09_mistake_correction_abstraction_level` — grounding and abstraction are **orthogonal axes**;
  store the failure **condition / reason / correction** as a triple. The candidate schema has
  `claim`/`evidence`/`bet` — no condition field.
- `icm-determinism-rule` — "Reflection retrieval is replayable iff, given the same corpus
  fingerprint and the same query, it returns the byte-identical chunk id set." **Already built**,
  and the mechanism this digest depends on.
- `00_measured_pre_registered_gate_s44` — "the decision must be designed before the evidence
  exists"; demote non-binding checks to diagnostics rather than letting them flip the verdict.

### Decision
Keep the grounding gate and the eviction phase. **Add an extraction constraint to the reflection
prompt:** every claim must be quotable from a chunk (already enforced) *and* every Decision must
name the file it will change. A Decision that cannot name a file is a self-narrative, and
`04_honest_lying_memory_confabulation` is precise about what that becomes. Separately, add a
`contrast` field to the candidate schema so a lesson records what it was contrasted against
(`01_09_mistake_correction_abstraction_level`'s condition/reason/correction triple, starting with
the cheapest third: the *condition*).

### Next bet
Add a gate line to `check_reflection.py`: reject any candidate whose `bet` field does not contain a
path-shaped token (`/`-separated, ending in a known extension or a script name). Falsifiable:
write one candidate with a prose-only bet — it must fail the gate. That negative control is the
proof, and it mirrors the project's own R3 from
`reflection/2026-09-15_provenance-stamp-enforced-spawn-hangs.md`: "validate a contract with its
negative controls, not just the happy path."

---

## Area 5 — Monitoring and logging problems

### Claim
Problem monitoring in this project is the strongest of the eight areas and it is strong for a
specific reason: every defect was found by *testing the invariant the pipeline claims*, not by
auditing for tidiness. But the loop is still open at one end — the lessons are recorded as
markdown postmortems (`reflection/2026-09-16_*.md`) and are **not queryable**, which is precisely
the failure `00_measured_closed_families_need_frontier_state` names: "a closed family written only
in prose is closed to a careful reader and open to everyone else."

### Evidence
- `reflection/2026-09-16_corpus-chunk-ids-not-unique.md` — R2: "the gate must check the invariant
  it depends on... Uniqueness of `id` across `knowledge/corpus/*.md` is a separate invariant and is
  currently untested." A defect found by probing an invariant, with a prevention rule routed to a
  named owning gate.
- `reflection/2026-09-16_gate-missing-imports-silently-stranded-manifest.md` — the gate crashed on
  every ingest since new call sites were added, and `ingest.py` **exited 0** because the crash was
  inside a nested call. "A failing gate reported success." This is the highest-value class of
  defect: a monitor that silently passes.
- `reflection/2026-09-15_manifest-gate-verified-reconstruction.md` — "A gate that regenerates its
  subject cannot detect that the subject is wrong." 240 of 596 chunks were attributed to phantom
  provenance while the gate passed.
- `reflection/2026-09-15_graph-identity-invariant-and-edge-deflation.md` — "The graph was built as
  a *cumulative* index, never audited as a *contract*"; "Existence ≠ addressability."
- `reflection/2026-09-15_provenance-stamp-enforced-spawn-hangs.md` — R1: "An unenforced contract
  is not a contract"; R2: "never call an orchestrator subprocess without a timeout."
- `00_measured_closed_families_need_frontier_state` — "Negative results need a queryable index,
  not just a record." Each entry must carry **magnitude**, not just verdict: "'REJECT' is not a
  finding."
- `00_measured_pre_registered_gate_s44` — "Make the gate reproducible from the harness, with a
  parity clause... This is what distinguishes 'I changed my interpretation' from 'I changed my
  data'."
- `00_08_lesson_persistence_eviction_requirement` — the two independent problems: wrong lessons
  (score-based eviction) vs volume (retrieval). Solving one does not solve the other.
- `09_memory_for_autonomous_llm_agents_mechanisms_eval` — "When an agent gives a wrong answer, was
  the problem in retrieval..." — the memory-survey form of the same diagnostic discipline.

### Decision
Keep the postmortem format and its trigger taxonomy (T1/T2/T3/T4). **Make the postmortems
queryable:** the corpus already contains the transferable rule — front-matter-tagged markdown
indexed by `build_graph.py`. The postmortems live in `reflection/` and are not in the corpus, so
the mechanism that would make them reachable is the one thing they are not connected to. The
smallest step is not a new system: it is adding each postmortem's *prevention rule* as a row in
the existing candidate ledger, which is already evicted and already gated.

### Next bet
Add a `check_postmortem_rule.py` sub-gate that asserts every `reflection/2026-*.md` postmortem has
an `R1` prevention rule *and* that the rule names an owning file. Falsifiable: run it against the
six existing postmortems — if all six already conform, the gate is free and the bet's value is in
the seventh postmortem; if any lacks a routed rule, the gate caught a real gap on its first run.

---

## Area 6 — Effective knowledge storing (structure + graph + automatic injection)

### Claim
This area is the most completely built and the one where the corpus most directly validates the
build. The three-layer structure (folder vocabulary / lossless corpus / graph index) is exactly
what `00_reflection_retrieval_dominates_write` calls "the configuration the benchmark does not
test: *lossless write + supplementary query-shaped index*." The missing piece is not storage or
retrieval — it is **injection is one-directional**. `GRAPH-DIGEST.md` is auto-injected into the
reflection agent; the reflection agent's *output* is not injected back into anything a future
working agent reads by default. Candidates are promoted by a separate script, not by the read
path.

### Evidence
- `00_reflection_retrieval_dominates_write` — retrieval moved accuracy 14–23 points vs write's
  3–8; raw chunks (zero LLM calls) matched or beat both lossy alternatives at 81.1% best overall.
  **Already built:** the corpus keeps full chunks with `source:` provenance; nothing is replaced
  by a summary.
- `00_reflection_closed_vocabulary_before_content` — identity is `uuid5(NAMESPACE_OID,
  f"{type}:{name}")`; no lookup, no ML; "the query path needs no LLM at all — a recursive CTE
  walks k hops in 2 ms"; "~400 tokens regardless of corpus size: growth is absorbed at build, not
  at query." This project's analogue is the content-addressed chunk id.
- `00_reflection_structure_substitutes_for_capability` — **the capability-conditional finding**:
  only the weakest model flipped wrong→correct; strong models reached the answer either way and
  the graph only changed their cost. "Do not record 'graphs beat search' — the strong-model rows
  refute it." This digest records the mechanism instead.
- `00_reflection_hybrid_retrieval_scale` — hybrid is corpus-scale dependent: hit@5 14.9% hybrid
  vs 16.3% dense on 500K passages, but 77.2% vs 73.4% on LoCoMo-scale memory. "at hundreds of
  chunks, keep the lexical leg; at hundreds of thousands of passages, distrust it." The corpus is
  at 633 nodes — firmly in the keep-the-lexical-leg regime.
- `00_agent_memory_hierarchies` — the write–manage–read loop coupled to perception/action;
  implication stated in the chunk: "treat `knowledge/corpus/*.md` + `knowledge/graph/graph.db` as
  the persistent hierarchical store (Layer 3 factory), and `knowledge/graph/ask.py` + digest
  injection as the managed read path." **Already built, and the chunk says so.**
- `00_persistent_memory_hierarchies_agents` — near-perfect LoCoMo models drop to 40–60% in
  MemoryArena: "passive recall ≠ decision-relevant use." **The injection gap is this finding:**
  the working agent must be prompted to *use* what is injected, not merely receive it.
- `00_icm_43_copies_four_moves` — copy-then-verify, originals stay until verified; decisions file
  gets one line per chat-trapped decision.
- `00_interpretable_context_methodology_folder_structu` — L0 identity / L1 routing / L2 stage
  contract / L3 factory / L4 working artifacts. **Already built** in this project's stage layout.

### Decision
Keep the three layers, keep the lossless corpus, keep the lexical leg. **Close the injection
loop:** an accepted candidate should be *writeable back* into a queryable surface that the working
agent reads by default, without a separate promotion step. The cheapest version is not a new
store — it is to have `promote_candidate.py` append the promoted rule to a single
`knowledge/GRAPH-DIGEST.md`-adjacent file that is already on the injection path. Per
`00_reflection_retrieval_dominates_write`, the promoted text must be indexed *alongside* the raw
chunk, never instead of it.

### Next bet
Wire `scripts/promote_candidate.py` so that an `accepted` candidate appends its rule (one line,
with the evidence chunk id) to a single rules file that `stages/04_reflect/CONTEXT.md` already
lists as an input. Falsifiable: after promotion, run `ask.py` for the rule's topic and assert the
rule's chunk id appears in the result set; if it does not, the promotion did not reach the read
path and the loop is still open.

---

## Area 7 — Effective graph building, blazing fast retrieval

### Claim
The graph is fast and deterministic because it refuses to be smart — and the corpus says that
refusal is the mechanism, not a limitation. The measured cost is already documented: 2 ms
recursive-CTE walk, ~400-token injection fixed at any corpus size. The project's own incident
history shows the real risk to that property is not query cost but **index inflation silently
degrading the one consumer**: 1.6M edges for 177k relationships, one node carrying 4,527 edges,
and `spawn_recursive.py`'s one-hop expansion returning 15,190 rows collapsing to 594 distinct
neighbors — 90.7% of all edges coming from tags selecting >25% of the corpus.

### Evidence
- `00_reflection_closed_vocabulary_before_content` — "Identity is content-addressed, so the build
  is deterministic and the traversal is reproducible. Because identity does not depend on a model
  judging similarity, the query path needs **no LLM at all** — a recursive CTE walks k hops in
  2 ms." Growth is absorbed at build, not at query.
- `00_reflection_structure_substitutes_for_capability` — the measured table (Haiku 1/3 hops wrong
  via search vs 3/3 via graph, 0 model calls, ~400 tokens) and the honest boundary: "One question,
  one corpus, no published variance — the flip could be noise even though the mechanism is real."
- `00_reflection_hybrid_retrieval_scale` — choose legs by corpus scale, not fashion; the
  re-measure trigger is "the corpus growing roughly an order of magnitude."
- `01_graph_memory_starter_inventory` — "Retrieval 2 ms; the ~400-token injection is fixed at any
  corpus size."
- `reflection/2026-09-15_graph-identity-invariant-and-edge-deflation.md` — D2: the edge inflation
  and its fix; "The index was paying 9.2× storage and query cost to carry information its only
  reader discarded." Also D1: id/stem drift, three cited chunks that could not be opened by the
  documented resolution path — "Existence ≠ addressability." **Already fixed**, with
  `build_graph.parse_chunk()` now enforcing `id == filename stem` at build time, verified by
  negative control.
- `icm-determinism-rule` — the three replayability conditions, including: "Content search is never
  load-bearing for citations... `bm25` ranking is not stable across schema or corpus changes. Tag
  intersection is the citation path; content search is discovery only." Observed again this
  session: `deterministic replay reproducible` matched zero chunks while the concept was reachable
  via tags.
- `00_agentic_rag_modular_graph` — keep the layers unmixed: "keep `knowledge/graph/graph.db` as
  the Graph RAG layer (SHARES_TAG edges + FTS5), `route.py --tag` as the deterministic retriever,
  and any external Exa/Jina fetch as the agentic retriever behind an explicit tool. Do not mix
  them implicitly in prompts." **Already built.**

### Decision
Keep content-addressed identity, exact-tag intersection with `ORDER BY id`, and the
hybrid-with-lexical-leg configuration. **Add an ongoing edge-economy gate:** a build-time check
that any tag selecting >25% of the corpus does not emit pair edges (or emits them at a
discrimination threshold). The fix was applied once, by hand; the invariant that prevents its
return is not currently checked.

### Next bet
Add a `--report` flag to `build_graph.py` (or a `check_graph_economy.py` gate) that emits, per
tag, selectivity and edge share, and fails when any single tag accounts for >25% of edges.
Falsifiable: run it on the current 633-node graph — if it passes, the hand fix held; if it flags
a tag, the inflation has returned. This is `00_measured_closed_families_need_frontier_state`'s
rule applied to the graph itself: record the *magnitude* (edge share), not the verdict.

---

## Area 8 — The dream: one unified graph brain, many sub-brains, automatic hierarchical routing

### Claim
The unified brain is **not** one graph. The corpus is unambiguous on this and it is the single
most important correction to the dream as stated. One-level routing is the measured optimum and a
second deeper routing level *never helped and sometimes broke accuracy outright*. A unified graph
with hierarchical sub-brain routing is a two-level router, and the controlled study says to build
one level. The right reading of "unified" is **unified identity and vocabulary, federated
storage**: one content-addressed id space and one closed vocabulary shared across sub-brains, so
a citation from the h720 brain resolves in the workspace-research brain, while each brain keeps
its own store, its own fingerprint, and its own eviction.

### Evidence
- `00_is_progressive_disclosure_all_you_need_for_long` — "A second, deeper routing level never
  helps and sometimes breaks accuracy outright, so one level is enough. Progressive disclosure
  buys context, not intelligence: it is redundant while a strong agent can locate the right
  passages itself, and decisive once the corpus grows too large to navigate by reading." The
  decisive constraint on the dream.
- `00_reflection_closed_vocabulary_before_content` — the ontology is fixed *before* any document;
  cognee's `namespace_entity_type_node_ids.py` migration and "deterministic key-based entity
  dedup via merged_into edges (SDK-208)" as framework-scale corroboration that the pattern is
  "an industry pattern, not a local trick." **This is what makes federation safe:** identity does
  not depend on a model judging similarity, so two brains can share an id space with no
  reconciliation step.
- `00_agentic_rag_modular_graph` — the taxonomy by cardinality/control (single-agent / multi-agent
  / hierarchical-corrective / graph-based) and the explicit instruction not to mix layers
  implicitly; "planner chooses retrieval strategy, executor grounds generation."
- `00_chief_of_staff_routing` — the Supervisor pattern: "cost drops when cheap deterministic lanes
  absorb 80% of traffic, but **misrouting costs more than not routing**, and the classifier needs
  visibility into downstream capabilities." The cost model for the router; also the reason a
  hierarchical router must be built *after* the capability map exists, not before.
- `00_reflection_hybrid_retrieval_scale` — "Neither study fixes the crossover scale; the trigger
  to re-measure is the corpus growing roughly an order of magnitude." A federated brain crossing
  that threshold must re-measure its legs, not inherit them.
- `00_reflection_structure_substitutes_for_capability` — capability-conditional: structure
  substitutes for capability at the small-model end and for cost at every tier. A sub-brain for a
  weak executor should be more structural; one for a strong orchestrator ("the workspace's own
  `ask.py` is the RAG half, which is correct *for a strong orchestrator*") should stay
  model-driven.
- `00_persistent_memory_hierarchies_agents` — the control plane is the missing piece: "learned
  controllers that decide *whether* memory is needed and *which* tier to query, rather than
  retrieving indiscriminately"; "Self-directed paging + active retrieval controllers are the
  missing control plane."
- `00_icm_43_copies_four_moves` — 43 side copies that never merged back; "Treat side
  copies/worktrees as drift signal, not source to auto-merge." **The anti-pattern for the unified
  brain:** federation by auto-merge is the failure the four-moves protocol exists to prevent.

### Decision
Reframe the goal as **unified identity + closed vocabulary + federated stores + one-level
routing**, not one graph with a hierarchy. Keep `route.py`'s flat alias expansion
(`decomposition`/`htn`/`pddl`/`classical-planning` in `knowledge/topics.md`) as the *entire*
routing hierarchy — that flat alias layer is the one level the evidence supports. Do not build a
router-of-routers. Build the shared id space and the shared vocabulary first, because
`00_reflection_closed_vocabulary_before_content` is explicit that this is the load-bearing and
cheap decision: "Fix the vocabulary first; everything downstream becomes mechanical."

### Next bet
Write one file, `knowledge/IDENTITY.md`, declaring the id rule (content-addressed, `id == filename
stem`), the shared vocabulary pointer (`knowledge/topics.md`), and the federation rule (each brain
owns its store + fingerprint + eviction; ids cross-resolve; nothing is auto-merged). Falsifiable:
a second brain (e.g. `projects/ts-ml-experiments`) can cite a workspace-research chunk id and have
it resolve — the one assertion federation depends on. If the id does not resolve, the vocabulary is
not actually shared and the dream is still one graph.

---

## Prior lessons (reflection_brain) — cited or contradicted

Queried: `python brains/reflection_brain/ask.py "workspace research planning horizon reflection
process problem logging" --limit 8`. The scars are the project's own accumulated history and are
not ignored; the three load-bearing ones are confirmed by this reflection, one is contradicted.

- **Confirmed — `S-s17-problem-lifecycle-no-circles` P1** ("a problem is 'solved for good' ONLY at
  `systematic_fix_applied` — a verified fix... AND a prevention invariant routed to a named owning
  doc"). This is exactly Area 5's finding and exactly Area 2's mechanism: a problem is closed by a
  *routed invariant*, not by a recorded verdict. `00_measured_closed_families_need_frontier_state`
  states the same rule ("Recording a verdict records that a thing was tried") and
  `00_measured_pre_registered_gate_s44` supplies the gate semantics.
- **Confirmed — `S-s17` P2** ("No plan, fix, or diagnosis starts without the Prior-Knowledge
  Check... a re-attempt of a listed failed approach without an explicit recorded reason... is a
  routing violation"). This is the *retrieval* side of Area 2's gradient: the frontier state is
  what makes the next step reality-based, and consulting it is mandatory, not optional reading.
- **Confirmed — `S-s15-reflection-brain-injection`** ("reflections were inert files — no automatic
  injection channel existed for scars... served through exactly the channels the active harness
  provides"). Area 6's injection gap is the same defect one layer up: injection exists for the
  corpus, not for the project's own accepted lessons.
- **Contradicted — `S-00-reflection-rules`** ("diagnostics live in logs, lessons live in
  `MONITORING/reflection/`"). Against the corpus, this is exactly the failure
  `00_measured_closed_families_need_frontier_state` names: prose-recorded lessons are "closed to a
  careful reader and open to everyone else." Diagnostics in logs and lessons in prose is the
  split that leaves the lesson unqueryable. Area 5's decision corrects it by routing the lesson
  into the gated candidate ledger.
- The `S-h720` scar (non-linear heads overfitting; held-out val superiority required) is the same
  discipline as `00_measured_pre_registered_gate_s44`, already cited in Area 2, and is not
  re-derived here — the h720 brain owns it.

---

## Decision (summary)

1. **Keep:** the 5-phase pipeline, the canonical `WORKFLOW.md`, exact-tag intersection routing with
   `ORDER BY id`, the lossless corpus beside the graph index, the lexical retrieval leg at this
   corpus scale, content-addressed chunk identity, the citation grounding gate, phase-5 eviction,
   one-level (flat alias) routing as the entire routing hierarchy.
2. **Change:** grade every plan step by its evidentiary basis and cut detail density with horizon
   (Area 2); change the ADAPT split trigger from cardinality to executor failure signal (Area 3);
   constrain reflection to artifact-extracted diagnosis and require each bet to name a file
   (Area 4); make postmortem prevention rules queryable rather than prose (Area 5); wire accepted
   candidates back onto the injection read path (Area 6); add an ongoing edge-economy gate (Area 7);
   add a vocabulary-reachability check (Area 1).
3. **Reframe:** the unified brain is unified *identity and vocabulary* over *federated* stores with
   *one-level* routing. Not one graph, not a router-of-routers (Area 8).
4. **The through-line:** every one of the eight areas is a closed loop at the artifact level with
   an open loop at the *read* level. The pipeline builds, gates, and evicts; it does not yet
   guarantee that what it validated is what the next agent will actually read. That is the single
   highest-value bet across all eight, and it is the one the corpus measured most precisely
   (`00_reflection_retrieval_dominates_write`: retrieval r = 0.98 against write strategy's 3–8
   points; `00_persistent_memory_hierarchies_agents`: "passive recall ≠ decision-relevant use").

## Next bet (the one that subsumes the rest)

A single new gate — `scripts/check_reachability.py` — asserting that (a) every question the working
agent is expected to ask reaches ≥1 chunk, and (b) every `accepted` candidate's evidence id is on a
read path the working agent actually reads. It is the smallest falsifiable step because it fails
loud on exactly the two conditions the corpus says are silent today: an unanswered question
(`00_reflection_closed_vocabulary_before_content`) and a validated lesson nobody reads
(`00_persistent_memory_hierarchies_agents`). Run it; if it exits 0, the read loop is closed and the
next bet is Area 2's `basis:` column; if it exits 1, the named gap is the next work.
