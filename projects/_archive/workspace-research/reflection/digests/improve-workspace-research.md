---
type: Concept
title: improve-workspace-research
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

fingerprint: 5f4f9d29057b  plan_version: ad0a031aa564  phase: 04_reflect  routing: see Routing section below
# Reflection: Improve workspace-research Pipeline (INBOX → corpus → graph → reflection)

- **fingerprint:** 1cf1e4aea87c (graph @ 581 nodes / 1593830 edges, via `knowledge/graph/GRAPH-DIGEST.md`)
- **routing queries used:** `python knowledge/graph/ask.py --tag icm --tag reflection --limit 10` (10 ids) + `python knowledge/graph/ask.py --tag context-engineering --tag planning --limit 10` (10 ids)
- **audit scope:** `INBOX/`, `knowledge/{corpus,graph,raw}/*.md`, `pipeline/06_reflect/`, `reflection/`, `scripts/`, `.omp/extensions/` — bounded ls only, ≤8 corpus expansions

---

## Verdict — Is the project ICM-sound?

**Mostly sound, not yet fully ICM-sound.** The filesystem-as-orchestrator, plain-text-as-interface, and deterministic routing invariants are implemented and produce a reproducible brain (`knowledge/graph/graph.db` = f(`knowledge/corpus/*.md`), fingerprint-gated). Progressive disclosure is wired via the `.omp/extensions/workspace-research.ts` 2000-char budget + `ask.py --tag` drill-down. What keeps it from "fully sound" are three closure gaps: (1) the determinism gate is advisory not enforcing, (2) reflection outputs lack an automated schema/closure gate on the write path, and (3) INBOX→corpus provenance is untraced across `knowledge/raw/` → `knowledge/corpus/`. All three are fixable without architectural change.

## Findings table

| # | Observed evidence (path) | Principle (chunk id) | Change |
|---|---|---|---|
| W1 | `pipeline/06_reflect/spawn.py` launches without calling `knowledge/graph/watch.py --once`; `.omp/extensions/workspace-research.ts` only emits a stale-digest warning (BUDGET 2000) | `00_interpretable_context_methodology_folder_structu` — ICM: graph is a pure derived index (f(corpus)), fingerprint gate before reasoning | Enforce `watch.py --once` at spawn entry; refuse to spawn if `.graph_fingerprint` ≠ digest fingerprint — turn warning into a hard gate (W1 high) |
| W2 | `knowledge/graph/GRAPH-DIGEST.md` (581 nodes truncated to 2000 chars by extension) + `knowledge/graph/ask.py` exact tag-intersection (`ORDER BY id`) | `00_is_progressive_disclosure_all_you_need_for_long` — one-level disclosure bound; second deeper routing level never helps, sometimes breaks accuracy | Keep one-level disclosure as the only expansion: mandate `ask.py --tag` intersection + optional single-hop edge expansion; forbid ad-hoc corpus browsing beyond returned ids, with CI check for un-cited claims |
| W3 | `reflection/digests/` + `reflection/candidates/` written by agents but `scripts/check_reflection.py` not wired into `pipeline/06_reflect/spawn_recursive.py` merge path; `pipeline/06_reflect/WORKFLOW.md` §5 closure check is manual | `00_memory_for_autonomous_llm_agents_mechanisms_eval` — reflection requires a verification loop/backpressure to persist | Wire `scripts/check_reflection.py` into `spawn_recursive.py` post-merge; reject digests with missing citations or unknown chunk ids before checkpoint |
| W4 | `pipeline/06_reflect/route.py` — static `tags LIKE` intersection `ORDER BY id` with no conditional expansion (observed deterministic but inflexible) | `00_adapt_as_needed_decomposition_and_planning_with` — ADAPT: as-needed decomposition/planning, expand only when needed | Add conditional edge-expansion: if intersection < threshold, expand top chunk via `graph.db` edges (`REFERS_TO`/`SHARES_TAG`) one hop deterministically; otherwise no expansion — adaptive without breaking determinism |
| W5 | `knowledge/raw/` (20 source files) → `knowledge/corpus/` (581 chunks) with no manifest linking raw→chunk ids (observed via `ls` counts) | `00_awesome_context_engineering` — context-engineering requires traceable ingestion and context offloading/quarantine | Generate `knowledge/raw/manifest.jsonl` mapping each raw source → derived corpus chunk ids via `scripts/ingest.py`; verify corpus hash covers raw sources |
| W6 | `INBOX/` empty directory, no `INBOX/issues.md`, no intake log; `pipeline/06_reflect/WORKFLOW.md` §0–1 assumes INBOX→corpus flow but leaves no provenance artifact | `00_from_plan_to_action_how_well_do_agents_follow_th` — plans/persistence fail without explicit state tracking | Implement INBOX deterministic cleanup invariant: `scripts/ingest.py` must log intake→corpus provenance to `knowledge/raw/` or `MONITORING/` and purge INBOX atomically after successful ingestion |
| W7 | No per-stage `CONTEXT.md` Inputs Table for `pipeline/06_reflect/` leaves; `knowledge/topics.md` provides tags but no stage contract names files to load (observed: `pipeline/06_reflect/leaves/*.prompt` without stage contracts) | `00_icm_map` — Five-Layer Context Hierarchy; L2 Stage Contract Inputs Table names exactly which L3/L4 files to load (single disclosure level) | Add a stage `CONTEXT.md` with Inputs Table for the reflection stage that explicitly lists allowed graph queries and leaf chunk sets, mirroring ICM L2 contract |
| W8 | `reflection/digests/icm-disclosure-depth-balance.md` holds C10 experimental (taxonomy depth ≠ disclosure recursion) pending `context-as-external-state.md` NB1 replay-pairing measurement (observed open question) | `00_icm_knowledge_big` — ICM knowledge persistence and "show your work" determinism; claims stay experimental until measured | Run NB1 replay-pairing regression (same task ± each ICM layer, measure output divergence) to promote or reject C10; decide whether folder depth is decorative vs load-bearing |

## Top 3 changes concrete

1. **W1 — Hard determinism gate (high, cheap, risk-reducing).** Edit `pipeline/06_reflect/spawn.py` to run `python knowledge/graph/watch.py --once` before building the prompt and compare `knowledge/graph/.graph_fingerprint` vs fingerprint parsed from `knowledge/graph/GRAPH-DIGEST.md` line 3. If mismatch, exit non-zero with `STALE_DIGEST` and refuse to launch `omp agent`. Also patch `.omp/extensions/workspace-research.ts` to expose the same check as a blocking error, not a warning. This closes the reproducibility hole with <20 LOC and makes every reflection digest fingerprint-decidable.

2. **W3 — Close the reflection verification loop (high, load-bearing).** In `pipeline/06_reflect/spawn_recursive.py` after the deterministic merge step, invoke `python scripts/check_reflection.py --digest reflection/digests/<topic>.md --candidates reflection/candidates/<topic>.jsonl` (schema: each candidate's `principle` id must exist in `graph.db`, every digest citation must resolve via `ask.py`). Gate the `git` checkpoint on this passing. This enforces the "every claim cites a returned chunk id" contract from `pipeline/06_reflect/WORKFLOW.md` §5 as code, not documentation.

3. **W5+W6 — Traceable ingestion with INBOX invariant (medium, foundational).** Extend `scripts/ingest.py` to emit `knowledge/graph/.ingest_manifest.jsonl` with rows `{raw_path, corpus_ids[], corpus_sha256}` and append an entry to `knowledge/topics.md` or a provenance file on each run. On success, atomically remove the consumed `INBOX/` artifact. Add a CI check `knowledge/raw/manifest vs knowledge/corpus/*.md` hash consistency. This restores ICM's externalized-state principle (state lives in files, not in agent memory) and makes the INBOX→corpus→graph chain auditable.
