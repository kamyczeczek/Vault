---
type: Concept
grade: active
title: CLAUDE
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# CLAUDE.md — research-engine

The autonomous loop: mutate forecasting architectures, discover new ones from
literature, and keep the knowledge index honest. Does not own any model — it
proposes them to `../benchmark-core` for evaluation.

## Where things live

| Path | Role | Description |
|---|---|---|
| `CLAUDE.md` | Catalog (L0) | This file |
| `CONTEXT.md` | Contract (L1) | Mutation cycle, leakage rules, promotion criteria |
| `mutation_engine.py` | Factory (L3) | Heuristic model mutation, emits proposals |
| `mutation_proposals.json` | Product (L4) | Current proposal queue |
| `research_engine.py` | Factory (L3) | `ModelDiscoveryEngine` + `AntiLeakageHarness` |
| `s47_ref/` | Reference (L3) | The S-47 mini-suite reference implementation |
| `evict_stale_reflections.py` | Factory (L3) | Drop reflections that no longer resolve |
| `sync_results_to_corpus.py` | Factory (L3) | Push results into the brain corpus |
| `query_kg*.py`, `check_*.py`, `read_kg_*.py` | Factory (L3) | Knowledge-graph query and inspection tools |

## Route by intent

| Intent | Go to |
|---|---|
| Propose a model mutation | `python mutation_engine.py` |
| Inspect the proposal queue | `mutation_proposals.json` |
| Discover models from the literature | `research_engine.py` |
| Query the knowledge index | `python kg.py resolve "<substring>"`, `expand <node-id> --steps N`, `resolve_and_expand "<substring>"` |
| Score the query surface | `python eval_kg.py` — harness vs LIKE baseline, log in `evals/` |
| Inspect reflections and memory | `query_kg_memory.py`, `query_kg_reflections_detailed.py`, `read_kg_reflections.py` |
| Evict stale reflections | `python evict_stale_reflections.py` |
| Push new results into the index | `python sync_results_to_corpus.py` |
| Check the corpus schema | `check_schema.py`, `check_tables.py` |
| Run the S-47 suite | `run_s47_suite.py` |
| Re-run S-47 with the expanding fit window | `python s47_ref/rolling_arm.py --window expanding` |
| Check whether the fit window changes the S-47 verdict | `python s47_ref/compare_window_policies.py` |
| Test the engine | `test_research_engine.py`, `test_kg_query.py` |

## Dependencies

- **On `../benchmark-core`** — a mutation is only worth keeping if it beats the
  incumbent there. This project proposes; that project decides.
- **On `../brain`** — the derived index this project queries and keeps fresh.

## Standalone

Run `python preflight.py` first; exit 1 lists exactly what is missing.
Siblings live under `$WORKSPACE_ROOT` (default: this project's parent,
i.e. `projects/research/`). Missing optional siblings (the graph, the incumbent
members, the archived series) degrade the tools; missing hard files
block the loop. What each sibling is used for: see `Dependencies`
above.

## Rules

- A proposal is a hypothesis. Nothing enters `../benchmark-core/members/` until
  it has beaten the incumbent on the evaluation protocol in that project's
  `CONTEXT.md`.
- The discovery engine must run its anti-leakage harness before reporting any
  accuracy number. A number that skips the harness is void.
- Stale reflections are evicted, not merged. Keeping a reflection whose evidence
  no longer resolves is how the index rots.
