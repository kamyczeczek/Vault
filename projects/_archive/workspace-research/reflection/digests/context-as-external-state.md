---
type: Concept
title: context-as-external-state
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

fingerprint: 5f4f9d29057b  plan_version: ad0a031aa564  phase: 04_reflect  routing: see Routing section below
# Reflection: Context as External Persistent State — ICM as its Concrete Instantiation

- **fingerprint:** 1cf1e4aea87c  (graph @ 581 nodes / 1,593,830 edges)
- **corpus reviewed:** 18 chunks across 12 source docs (ICM paper + map, Plans-Don't-Persist, Progressive-Disclosure, Memory survey, ADAPT, From-Plan-to-Action, Enhancing-via-Global, Self-Evolving-World-Models, Improving-Planning/MAP, DEX interview, Real-Design-Patterns, awesome-context-engineering, Why-Benchmarks-Don't-Mean)
- **method:** graph-injected digest → `ask.py` cross-axis retrieval → targeted chunk reads → evidence-first synthesis
- **scope:** cross-cutting *principles*, not a single paper summary

---

## TL;DR (the claim)

The corpus converges on one load-bearing thesis:

> **Agent reliability is gated by treating context as explicit, persistent, scoped, and verifiable *external* state — not as transient model-internal memory.** ICM (folder-structure-as-orchestrator) is the corpus's most concrete instantiation of this thesis; the empirical papers supply the *why* (models don't persist what they don't see) and the *bounded limits* (disclosure helps but doesn't add intelligence; plans decay if evicted).

Every high-value chunk independently points at the same failure mode — **context that silently drops, leaks, or gets overloaded — and the same remedy — externalize it to files/skills/structured state.**

---

## Evidence map

| Chunk (id) | Proves |
|---|---|
| `00_interpretable_context_methodology_folder_structu` | ICM thesis: filesystem *is* orchestrator; one agent reads right files; local scripts do non-AI work. Replaces framework overhead for sequential human-reviewed flows. |
| `00_icm_map` | ICM "Five Rules": One-Stage-One-Job, Plain-Text-Interface, Layered-Context-Loading, Every-Output-is-Edit-Surface, Configure-the-Factory-not-the-Product. Lineage: Unix pipes, multi-pass compilers, literate programming, lost-in-the-middle. |
| `00_plans_don_t_persist_why_context_management_is_lo` | **Hard evidence:** standard LLM agents do *not* carry plans as persistent state. Plan signal spikes to 0.453 step-1 then falls 4.1× in one step; naive eviction cuts ALFWorld success 34.7pp. "Agent-critical info can be context-resident rather than persistent." |
| `00_is_progressive_disclosure_all_you_need_for_long` | Controlled study: progressive disclosure **buys context, not intelligence**. Redundant when a strong agent already locates passages; decisive when corpus too big to read. **One level is enough; a 2nd routing level never helps and sometimes breaks accuracy.** |
| `00_memory_for_autonomous_llm_agents_mechanisms_eval` | Formalizes memory as write–manage–read loop; taxonomy of 5 mechanism families. Closes with open challenges: continual consolidation, causally-grounded retrieval, **trustworthy reflection**, learned forgetting. |
| `00_adapt_as_needed_decomposition_and_planning_with` | ADAPT: decompose *as-needed on executor failure*, not upfront. +28.3% ALFWorld / +33% TextCraft over non-adaptive plan-and-execute. Implication: static decomposition is fragile; adaptivity must be externalized into the control loop. |
| `00_from_plan_to_action_how_well_do_agents_follow_th` | At scale (21,120 SWE-agent trajectories): plan is *advisory only*; compliance decays as context fills. Periodic plan reminders mitigate. **Subpar plan hurts more than no plan.** Plan and execution context must be re-anchored, not written once. |
| `12_enhancing_llm_based_agents_via_global` | Global/GoalAct vs ReAct: monolithic context (too many tools in one code block) fails; explicit goal-state compression works. Context *shape* changes success, independent of model. |
| `33_improving_planning_with_large_language` | MAP (multi-module planning) solves 74–77% vs ToT 6%; key is *cached, externalized* module results (Actor/Decomposer excepted). External state reuse >> raw model reasoning. |
| `20_self_evolving_world_models_for_llm_agent_plannin` | World models = externalized transition memory (retrieved past `(s,a,o)`); reflection prompt forces explicit state-vs-goal reasoning. External reflection surface improves planning. |
| `02_jak_naprawd_wycisn_2_3x_z_ai_w_kodowaniu_na_pods` | Practitioner synthesis: leverage (specification) + context hygiene + verification (tests) + model economy = the 2–3×. "Context window hygiene / fighting the stupidity zone" is named as a first-class lever. |
| `02_real_design_patterns_for_agentic_software_factor` | "Don't chase models — build good systems"; define interfaces; trust nothing from users—verify in pipeline; design for human intervention; build for swapability. Architecture > model. |
| `02_awesome_context_engineering` | Field consensus: most failures are *context*, not model; compaction is **lossy**; avoid fragile parallel multi-agent context; harness layer is a first-class control surface. |
| `02_why_passing_benchmarks_doesn_t_mean_your_ai_wrot` | No fast scalable judge for "good code" → models trained on RL optimize short-horizon, not long-horizon engineering. Division of labor: AI does well-defined one-offs; humans own long-term architecture. |

---

## Synthesis

Three strata reinforce each other:

1. **Empirical WHY (models are context-resident, not persistent).** Plans-Don't-Persist and From-Plan-to-Action show agents re-read rather than internalize: drop the text and behavior silently breaks. This is the *mechanism* behind every "context rot / lost-in-the-middle / compaction loss" report in the field-consensus chunk.
2. **Structural remedy (externalize, scope, re-anchor).** ICM's five rules, ADAPT's as-needed decomposition, MAP's cached modules, and world-model transition memory are four independent implementations of the *same* move: put the load-bearing state **outside the model**, in files / skills / structured stores, and refresh it on a schedule the *system* controls (not the model's attention).
3. **Bounded limits (don't over-engineer the externalization).** Progressive-Disclosure proves one disclosure level suffices and a second can hurt; the DEX and Real-Design-Patterns chunks warn that chasing models or building fragile parallel multi-agent context backfires. Externalization has a goldilocks zone: enough to survive eviction, not so much it becomes its own context-pollution problem.

**Conclusion:** ICM is not one framework among many — it is the corpus's canonical answer to the empirically-demonstrated context-residency failure. The open work is making ICM's *implicit* invariants explicit and *testable*, and bounding its externalization depth.

---

## Candidate principles (state-machine verdicts)

Full machine-readable records in `candidates/context-as-external-state.jsonl`. Summary:

| id | principle | verdict | key evidence |
|---|---|---|---|
| C1 | External-Persistence: load-bearing state lives in files/stores, not model memory | **accepted** | `00_plans_don_t_persist…`, `33_improving_planning…` (cached modules), `20_self_evolving_world_models…` |
| C2 | Scoped-Context: load only what the current stage needs | **accepted** | `00_icm_map` (Layered-Context-Loading), `00_one_stage_one_job`, `00_is_progressive_disclosure…` |
| C3 | Determinism-Evidence: emitted artifacts must be reproducible/verifiable | **accepted** | `02_why_passing_benchmarks…`, `02_real_design_patterns…` ("trust nothing—verify"), `00_plain_text_as_interface` (git-diffable) |
| C4 | Progressive-Disclosure bounded to one level | **experimental** | `00_is_progressive_disclosure…` (2nd level hurts) — needs replication beyond ∞Bench/book-QA |
| C5 | Single-agent + external orchestration over fragile parallel multi-agent context | **experimental** | `02_awesome_context_engineering` (Cognition "don't build multi-agents"), `02_real_design_patterns…` — strong field signal, few controlled studies |
| C6 | Plan-Residency-Shield: persist/re-anchor plan+invariants across eviction | **experimental** | `00_plans_don_t_persist…` (replay-pairing diagnostic), `00_from_plan_to_action…` (periodic reminders help) |
| C7 | Human-in-the-loop as edit surface at every stage | **accepted** | `00_icm_map` (Every-Output-is-Edit-Surface), `02_real_design_patterns…` (design for intervention) |
| C8 | Model-economics tiering (reserve frontier for design, cheap for execution) | **accepted** | `02_jak_naprawd…` (strategic model use), `02_real_design_patterns…` (Opus for UI, Codex for execution) |
| C9 | Context-budget as first-class metric (track tokens/invariants surviving eviction) | **proposed** | implied by `00_plans_don_t_persist…` probe method; no corpus chunk states it as a standing practice |

---

## Open questions / gaps in the corpus

1. **No controlled study of ICM-vs-framework outcomes.** ICM is argued (architecture, lineage) but the corpus has no A/B of ICM folder-orchestration vs LangChain/AutoGen on a real task. ADAPT/MAP are the closest *externalized-state* validators but use code frameworks, not filesystem orchestration.
2. **Replay-pairing not yet turned into an ICM invariant test.** Plans-Don't-Persist gives a diagnostic (cosine distance with/without plan); nobody applies it to a file-based pipeline's "did the stage re-read its CONTEXT.md" question.
3. **Corpus is skewed to sequential/human-reviewed workflows.** ICM explicitly scopes there; concurrent/multi-agent context (Manus Wide-Research, Cognition) is only noted as "avoid," not characterized with evidence inside this KB.
4. **Reflection trustworthiness under-specified.** Memory survey lists "trustworthy reflection" as open; nothing in corpus defines how to verify a reflection agent's output (which is exactly this agent's job — see Next Bet 3).
5. **Compaction loss is named but not measured in-KB.** awesome-context-engineering flags lossy compaction; Plans-Don't-Persist measures eviction cost on *plans* but not on summarized history.

---

## Next bets

- **NB1 (experiment, addresses OQ1/OQ2):** build a minimal ICM pipeline (2–3 staged folders + local script) and run a *replay-pairing-style* regression: same task with vs without each stage's CONTEXT.md present; measure output divergence. If divergence ≈ 0, the stage is decorative (violates C1); if large, C1/C6 hold for filesystem orchestration too. Cheap, decisive, corpus-grounded.
- **NB2 (corpus gap):** ingest 1–2 controlled multi-agent-vs-single-agent context studies to promote C5 from experimental→accepted or reject it. Currently C5 rests on one blog + practitioner访谈.
- **NB3 (meta, addresses OQ4):** define a *reflection acceptance contract* for this very folder — every `digests/*.md` must cite ≥3 chunk ids and every `candidates/*.jsonl` record must carry `evidence_ids`. This makes C3 operational for the reflection process itself.
- **NB4 (proposed→experimental):** pilot C9 by logging context-budget per stage in a future run (tokens in CONTEXT.md vs tokens surviving to output) — turns "context hygiene" from intuition (DEX chunk) into a tracked metric.

---

*Generated by reflection agent over graph `1cf1e4aea87c`. Writes limited to `reflection/digests/` and `reflection/candidates/`. No corpus/source edits.*
