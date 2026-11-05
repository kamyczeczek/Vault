---
type: Concept
title: phase2_simplicity_db
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# VERA Phase 2 Direction: Simplicity, Understandability, and DB-Integrated Workflow

Set 2026-09-24 from researcher direction: research into (a) simplicity/easiness-of-
understanding as performance drivers, (b) merging the workflow more tightly with the graph
database. Each thrust is a falsifiable experiment, not an opinion.

## Source map (retrieval-bounded)

- Simplicity/minimalism: `00_karpathy_minimalist_agentic_coding_harnesses`,
  `00_00_bend2_vibe_coding_reinventing_wheels` ("don't reinvent the wheel"),
  `03_why_performance_engineering_breaks_ai_coding_agent` (performance as loop; every
  bottleneck slows the whole system), `00_a_complete_guide_to_managing_thousands_of_files`
  (ICM "one folder, no rot" simplicity)
- Understandability → performance: `00_reflection_reorientation_cost` (bounded state +
  query beats growing files — the key mechanism), `00_workspace_rapid_understanding`,
  `00_plan_persistence_context_window_compaction` (context rot degrades everything)
- DB-integration: `00_graph_database_architectural_reflection` (hybrid FTS5 + local
  embedding index proposal), `knowledge/graph/context_gateway.py` (existing primitive —
  the lab already HAS a gateway; Phase 2's job is to make the workflow route through it),
  `01_00_software_factory_isolate_build_prove_ship` + `reflection_rule_of_scars`
  (context gateway with fast/default/deep token budgets)

---

## Experiment SIM-1: Simplicity ablation (fewer gates, same quality?)

Hypothesis: **at equal evidence quality, a stripped workflow (fewer gates, single retrieval
path) costs less and is faster to first answer — and the complexity in the current lab is
payable, not ceremonial.** (Counter-hypothesis: some gates are load-bearing; ablation
locates which.)

Design:
- Arms: (S0) full current pipeline (stages 00–06, all 15 gates) · (S1) minimal: retrieve →
  answer → 1 external-verification gate · (S2) no-gate single pass (B0.1-like).
- Fixed task set: L1 questions (Q1–Q4) + 2 L2 questions.
- Metrics: time-to-first-answer, total tokens, integrity (claim support ratio),
  rework rate (answers invalidated downstream), wall-clock per gate.
- Verdict rule: S1 ≥ S0 on quality AND ≤0.5× cost → complexity is payable; gate-by-gate
  ablation table identifies the load-bearing gates to keep.

## Experiment SIM-2: Cold-start understandability test

Hypothesis: **ease of understanding (a new session's reorientation cost) predicts downstream
performance** — sessions that orient faster on a "simple" orientation set answer with fewer
retrieval ops and fewer ungrounded claims.

Design:
- Two orientation packs: (A) full contract set (CONTEXT.md + stage CONTEXTs, ~current state)
  · (B) a distilled one-page pack (core loop + invariants + command list, "easiness" version).
- Cold-start protocol: fresh session (no prior history), first task = answer Q1 verbatim
  with correct citations.
- Metrics: tool calls to first valid answer, token cost to first valid answer, ungrounded-
  claim rate on that answer, reorientation time.
- Verdict rule: B wins on all 3 by ≥30% without integrity loss → distill-and-simplify is
  a promotion candidate for the lab's onboarding (meta-evolution loop: the lab's own docs
  get simpler because it measured itself).
- Key mechanism tracked: **bounded state + query over growing files**
  (`00_reflection_reorientation_cost`) — the simple pack must route to the graph for depth,
  not duplicate it.

## Experiment DB-1: Single-graph read path

Hypothesis: **routing workflow reads through one graph interface (ask.py /
context_gateway) instead of ad-hoc file crawling lowers token cost and eliminates stale
reads, with no recall loss on seeded questions.**

Design:
- Arms: (D0) agent free to crawl files (current reality of some subagents) · (D1) agent
  constrained to ask.py + context_gateway only (files read only through gateway excerpts).
- Fixed task set: same 6 questions as SIM-1, plus a **freshness probe**: ingest one chunk,
  ask a question touching it, measure time-to-first-visible (staleness detection).
- Metrics: tokens to first valid answer, number of full-file reads (target: →0 in D1),
  recall on seeds (must match D0), freshness time-to-visible, stale-read incidents (D0
  expected to have some; D1 expected zero).
- Verdict rule: D1 = D0 recall AND ≥50% token reduction AND zero stale reads → adopt
  gateway-only as lab policy (06_meta_evolve candidate). Follow-up work item: extend
  context_gateway with the `00_graph_database_architectural_reflection` hybrid proposal
  (local embedding index alongside FTS5) only if D1 shows lexical recall ceilings.

## Ordering and shared rules

1. SIM-1 first (defines what "simple" means measurably), then SIM-2 (uses SIM-1's minimal
   arm as pack B baseline), then DB-1 (its "free crawl" arm reproduces whatever the lab
   actually does today — captured, not assumed).
2. All arms run on the frozen fingerprint (current: 05bc79e4b41e — re-pin after B0.2 pass).
3. Simplicity claims need the same negative controls as everything else in VERA: a
   "simpler" arm that drops a load-bearing gate must show integrity regression or the
   simplicity verdict is void.
4. Each experiment's winner feeds `reflection/candidates/` with the ablation table as
   evidence — the meta-evolution loop closing on the lab's own workflow, as designed.

## Seeds for the three new L4/L5 questions (Q21–Q23, to add to benchmark after freeze)

- Q21 (L4): "Which stage gates in this lab are load-bearing vs ceremonial, per ablation?"
  seeds: 00_karpathy..., 03_why_performance..., 00_00_bend2...; distractors: 24_agentforce...
- Q22 (L4): "Causal chain: how does reorientation cost convert to performance loss?"
  seeds: 00_reflection_reorientation_cost, 00_workspace_rapid_understanding;
  distractors: 00_session_compaction (adjacent, different lever)
- Q23 (L5): "Design the single-graph read path for all lab stages; spec the gateway API
  and the policy that forbids direct file reads."
  seeds: 00_graph_database_architectural_reflection, 01_00_software_factory...;
  distractors: 76_graph_databases_new_opportunities (DB theory, not this lab)
