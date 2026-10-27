---
type: Concept
title: workspace-health
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

fingerprint: 5f4f9d29057b  plan_version: ad0a031aa564  phase: 04_reflect  routing: see Routing section below (regenerated after corpus tag repair)
# Reflection: Workspace Health — workspace-research (graph `35b86bc954fa`, 596 nodes / 1632751 edges)

- **Routing contract:** every claim cites a chunk id returned by `python knowledge/graph/ask.py --tag <t1> --tag <t2> --limit 12` (deterministic `ORDER BY id` intersection). No free recall.
- **Queries executed for this digest:**
  - `icm+observability` → `00_chief_of_staff_routing`, `00_hooks_board_events`
  - `icm+planning` → `00_agent_memory_hierarchies`, `00_agentic_rag_modular_graph`, `00_chief_of_staff_routing`, `00_hooks_board_events`, `00_icm_knowledge_big`, `00_icm_map`, `00_interpretable_context_methodology_folder_structu`, ...
  - `context-engineering+reflection` → `00_icm_43_copies_four_moves`, `00_agent_memory_hierarchies`, ...
  - `context-engineering+memory` → `00_agent_memory_hierarchies`, `00_persistent_memory_hierarchies_agents`, ...
  - `icm+hooks` → `00_hooks_board_events`, `planning-with-files-pattern`
  - `icm+reflection` / `agentic+planning` / `context-engineering+anti-leakage` as above
- **Workspace inspected:** `INBOX/`, `knowledge/{corpus,graph,raw}`, `reflection/{candidates,digests}`, `pipeline/06_reflect/`, `stages/`, `stages01_inbox`..`stages04_reflect`, `scripts/`, `.omp/extensions/`.

---

## Claim / Evidence / Decision / Next bet

### 1. Filesystem-as-orchestrator is intact — but shadow folder names are a routing drift hazard

- **Claim:** The ICM invariant "filesystem is the orchestrator; one agent reads the right files at the right CONTEXT.md" holds logically, but physical layout has drift: `stages/` (correct `01_inbox/..04_reflect/`) coexists with legacy siblings `stages01_inbox/`, `stages02_corpus/`, `stages03_graph/`, `stages04_reflect/` at repo root. A fresh agent cold-walking via `CONTEXT.md` can route to the empty shadow dirs.
- **Evidence:** `00_interpretable_context_methodology_folder_structu` (ICM paper §1), `00_icm_map` (L0 identity → L1 routing → L2 stage contract), `00_one_stage_one_job` (single-responsibility-per-folder), `00_icm_43_copies_four_moves` (proposal gate + copy-then-verify + cold-walk test; 43 copies counted as drift signal).
- **Decision:** Keep `stages/` as canonical. Remove or gitignore the four shadow dirs after verifying they are empty/unreferenced — do not touch `knowledge/` or `reflection/`.
- **Next bet:** `rmdir stages01_* stages02_* stages03_* stages04_*` after `grep -R stages01` shows zero refs; then re-walk `CONTEXT.md` cold-start as the gate in `00_icm_43_copies_four_moves`.

### 2. Determinism: fingerprint exists but gate is advisory — stale digest can be consumed silently

- **Claim:** The derived-index contract "`graph.db` = f(`corpus`), fingerprint-gated before reasoning" is implemented yet not enforced: `knowledge/graph/GRAPH-DIGEST.md` carries `fingerprint: 5f4f9d29057b` but neither `pipeline/06_reflect/spawn.py` nor `.omp/extensions/workspace-research.ts` refuses to reflect on mismatch — they warn.
- **Evidence:** `00_interpretable_context_methodology_folder_structu` (graph is pure derived index), `00_agent_memory_hierarchies` (manage = compression/consolidation with fingerprint; build_graph fingerprint), `00_is_progressive_disclosure_all_you_need_for_long` (disclosure discipline bounds), `00_pocock_context_shared_language` / `00_pocock_writing_for_agents` (shared language + writing-for-agents determinism).
- **Decision:** Keep design, harden gate. Require `watch.py --once` (or equivalent fingerprint equality) at reflection entry; refuse to write to `reflection/` on `STALE_DIGEST`.
- **Next bet:** Patch `pipeline/06_reflect/spawn.py` (~15 LOC) to compare `knowledge/graph/.graph_fingerprint` vs parsed digest fingerprint before `omp agent` launch; promote extension warning to error.

### 3. Observability: hook primitives are documented but not wired — pipeline runs headless

- **Claim:** The corpus prescribes non-blocking hooks as the observability layer (`hooks-board-events` → `board/events.jsonl` + `board/index.html`), but this workspace has no hook wiring for ingestion or reflection leaves — failures leave no lane trace.
- **Evidence:** `00_hooks_board_events` (PreToolUse/PostToolUse → `board/events.jsonl`, never blocks), `00_chief_of_staff_routing` (CLAUDE.md + `.claude/agents/` + `route.py --tag` as routing contract), `planning-with-files-pattern` (task_plan + findings + progress on disk, hooks as re-injection).
- **Decision:** Add a minimal `PostToolUse` hook on `Write`/`Agent` that appends to `reflection/leaves/events.jsonl` for the `spawn_recursive.py` path; keep it non-blocking and poll with static `board/index.html`.
- **Next bet:** Wire one hook file + one JSONL; gate separately via `watch.py` + `scripts/check_reflection.py` — no enforcement in the hook.

### 4. Reflection closure: a dedicated stage exists yet its Inputs Table is underspecified

- **Claim:** `pipeline/06_reflect/` exists with `WORKFLOW.md` + `route.py` + `spawn_recursive.py` + leaves, satisfying the per-stage context contract in principle, but the stage's Inputs Table does not explicitly enumerate allowed `ask.py --tag` intersections and leaf chunk sets — leaving re-anchoring to convention.
- **Evidence:** `00_icm_map` (L2 Stage Contract Inputs Table names exactly which L3/L4 files to load), `00_one_stage_one_job` (stage sizing / single job), `00_plain_text_as_interface` (plain-text interface; Inputs/Process/Outputs).
- **Decision:** Keep the stage, tighten the contract: list allowed tag intersections per reflection topic in the stage contract (or `WORKFLOW.md` § inputs).
- **Next bet:** Add an Inputs Table to `pipeline/06_reflect/WORKFLOW.md` or `stages/04_reflect/CONTEXT.md` mirroring `stages/01_inbox/CONTEXT.md` shape.

### 5. Memory: persistent hierarchical store is correctly externalized — replay-pairing diagnostic remains unapplied

- **Claim:** Persistent memory is externalized correctly (`knowledge/corpus/*.md` + `knowledge/graph/graph.db` as L3 factory; `knowledge/graph/ask.py` + digest injection as managed read path; `INBOX/` → `scripts/ingest.py` → `knowledge/corpus/` as write path). The gap is diagnostic: the Plans-Don't-Persist replay-pairing method is not turned into a health check for pipeline outputs.
- **Evidence:** `00_agent_memory_hierarchies` (write–manage–read + hierarchical store), `00_persistent_memory_hierarchies_agents` (persistent hierarchies), `00_plan_persistence_context_window_compaction` (compaction evicts plans), `00_plans_don_t_persist_why_context_management_is_lo` / `00_from_plan_to_action_how_well_do_agents_follow_th` (plan residency shield — cosine/probe diagnostics).
- **Decision:** No store change. Add a replay diagnostic: same task with vs without each stage's `CONTEXT.md` present, measure output divergence; divergence≈0 means stage is decorative.
- **Next bet:** Pilot on one leaf topic (≤1h) before codifying as a health metric.

### 6. Anti-leakage / durability: low current leakage, no evidence of long-term decay yet

- **Claim:** No drift signals at scale were observed beyond the shadow dirs (single empty `INBOX/`, digest current at `35b86bc954fa`, `reflection/` outputs paired `digests/*.md` ↔ `candidates/*.jsonl`, `scripts/check_reflection.py` validates state machine). Long-term anti-leakage depends on periodic reinforcement, which has no scheduled surface in this quiet repo.
- **Evidence:** `00_icm_43_copies_four_moves` (43 side copies as leakage detector; decisions trapped in chats), `00_from_plan_to_action_how_well_do_agents_follow_th` (plan compliance decays without reminders; periodic re-anchoring), `00_plans_don_t_persist_why_context_management_is_lo` (naive eviction 34.7pp drop).
- **Decision:** Accept health as good at this snapshot; schedule re-anchoring by re-running reflection on isolation/observability criteria next cycle.
- **Next bet:** Promote `scripts/review_gate.py --phase before/after` logging around the next reflection insertion to make decay measurable.

### 7. Reflection workflow itself is load-bearing — verification loop must remain enforced

- **Claim:** This reflection's own credibility rests on the verification loop (`scripts/check_reflection.py` validating every digest citation resolves in `graph.db` and every `candidates/*.jsonl` record satisfies `{id,state,claim,evidence,bet}` with valid state `proposed→experimental→accepted|rejected`). Without it, reflection outputs are unverifiable prose.
- **Evidence:** `00_memory_for_autonomous_llm_agents_mechanisms_eval` (trustworthy reflection as open challenge), `00_pocock_grilling` (grilling as verification discipline), `00_icm_43_copies_four_moves` (cold-walk + final-move verification).
- **Decision:** Keep the gate wired post-merge in `spawn_recursive.py` (already proposed as W3 in `reflection/digests/improve-workspace-research.md`); do not relax citation rules.
- **Next bet:** Run `python scripts/check_reflection.py` in CI and as the reflection stage's closure check — reject digests with missing citations or unknown chunk ids.

---

## Overall verdict

**Workspace is healthy and ICM-sound at the contract level; friction is operational.** Determinism, routing, disclosure, plain-text interface, and externalized memory are implemented and produce a reproducible brain. The open load is the last-mile gates: stale-digest refusal, shadow-dir cleanup, hook observability, Inputs Table specificity, and the replay diagnostic. No architectural change required — each is a small, reversible move behind an existing gate (`watch.py`, `check_reflection.py`, cold walk).

*Generated by reflection agent `workspace-health` over digest `35b86bc954fa` (596 / 1632751). Writes limited to `reflection/digests/` + `reflection/candidates/`. No corpus/source edits.*
