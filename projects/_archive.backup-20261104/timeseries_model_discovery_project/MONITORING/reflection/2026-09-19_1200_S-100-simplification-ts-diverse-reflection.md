---
type: Concept
title: 2026-09-19_1200_S-100-simplification-ts-diverse-reflection
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Reflection — 2026-09-19_1200_S-100-simplification-ts-diverse-reflection
Date: 2026-09-19
Status: complete
Invoking rule: REFLECTION_RULES.md (T4, T1)

## work_summary
User requested reflection on simplifying this project, using `C:\Users\Mateusz\Desktop\ROOT\projects\ts-diverse` as the reference experience surface, while continuing time series model experimentation. Investigated ROOT's isolated-brain injection pattern, ts-diverse's standalone fast-bench design, and the current project's stage/gate load. Delivered this reflection with concrete simplification actions and an experiment continuation path.

## problems
### P1: stage/gate machinery dominates model-iteration cost
- **symptom:** Every task must traverse up to 7 stage folders and commit-time gates before a model idea is scored.
- **root_cause:** `PROCESS/WORKFLOW.md` treats all work as full-stage ICM pipelines; there is no lightweight “experiment mode” for fast model probes.

### P2: knowledge injection is manual, not automatic
- **symptom:** The agent must run `python brain/ask.py ...` explicitly; no prompt-time injection occurs during normal conversation.
- **root_cause:** ROOT shows the workable pattern (`workspaces/<brain>/.omp/extensions/<brain>.ts` appending scar/graph digests), but this project only has `brain/` files and `PROCESS/07_reflect/CONTEXT.md` query contract — no worker extension.

### P3: ETTh1 H720 saturation blocks new signal
- **symptom:** `PROGRESS.md` shows incumbent MAE 1.9781 and multiple REJECTED bets (S46/S48).
- **root_cause:** The current project evaluates almost exclusively on one dataset/horizon; cross-domain generalization is unmeasured.

### P4: experiment artifacts are heavyweight
- **symptom:** ts-diverse delivers a full benchmark in `bench.py` with `members/` and `results/`; this project's experiments require `rolling_arm.py`, registry edits, leaderboard updates, and stage artifacts.
- **root_cause:** Experiment plumbing is coupled to the H720 rolling-origin protocol and skills/routing machinery.

## solutions
### P1
- **solution:** Introduce `PROCESS/08_experiment/CONTEXT.md` with a lightweight experiment contract: single script under `experiments/`, no mandatory stage walk, optional close reflection, no registry edit required. Full-stage route remains for incumbents/merges.
- **verification_evidence:** `read PROCESS/08_experiment/CONTEXT.md` after authoring; gate smoke via `python PROCESS/run_gates.py --quiet` once row added to workflow routing table.
- **files_changed:**
  - `PROCESS/WORKFLOW.md` (add Experiment mode + stage mapping)
  - `PROCESS/08_experiment/CONTEXT.md` (new lightweight contract)

- **solution:** Add `brain/worker/.omp/extensions/ts-brain.ts` as an opt-in extension for isolated ts-brain worker sessions only. It injects the current leaderboard + `brain/internal/digest.md` into worker prompts when the agent is started with `--cwd brain/worker`; the main orchestrator agent remains clean. Model after ROOT's isolated-brain worker; scope it to this project's h720/ts-ml graph only.
- **verification_evidence:** `node --test PROCESS/05_verify/test_ts_brain_injection.mjs` exercises callback seam and asserts injected snippet contains leaderboard row and digest header; main-agent prompt remains unchanged without the worker cwd.
- **files_changed:**
  - `brain/worker/.omp/extensions/ts-brain.ts` (new)
  - `PROCESS/05_verify/test_ts_brain_injection.mjs` (new)
  - `brain/internal/` assets remain authoritative; extension resolves them module-relative.

### P3
- **solution:** Continue ts-diverse-style cross-domain probing in parallel: import `projects/ts-diverse/bench.py` task suite as a secondary validation surface for promising candidates before committing them to H720 rolling evaluation.
- **verification_evidence:** `cd projects/ts-diverse && python bench.py` exits 0 and produces `results_s47.json` + `harness.log`; a candidate accepted by both H720 rolling and ts-diverse mean-rank gets promotion weight.
- **files_changed:**
  - reuse existing `projects/ts-diverse/`; no required edits.

### P4
- **solution:** Create `experiments/playground.py` that mirrors `ts-diverse/bench.py` shape: task list, fit/predict members, rolling_preds helper, pool blend, JSON/harness output. Keep it NumPy-only; no torch/h720 registry required.
- **verification_evidence:** `python experiments/playground.py --smoke` runs 2-task synthetic suite in <10s and writes `experiments/output/smoke_results.json`.
- **files_changed:**
  - `experiments/playground.py` (new)
  - `experiments/README.md` (new)

## prevention_rules
### P1
- **invariant:** Fast model probes MUST be routable through a single experiment stage/contract; full-stage ICM routing is reserved for incumbents, merges, and contract changes.
- **owning_doc:** `PROCESS/WORKFLOW.md`
- **owning_doc_updated:** Y

### P2
- **invariant:** Worker-scoped prompt injection MUST be implemented as an isolated `.omp/extensions/<brain>.ts` file resolved module-relative, activated ONLY for agents started with `--cwd brain/worker`; the main orchestrator agent MUST NOT receive automatic brain injection.
- **owning_doc:** `AGENTS.md`
- **owning_doc_updated:** N

### P3
- **invariant:** Any candidate promoted to incumbent MUST be validated on at least one cross-domain mini-suite in addition to the primary H720 leaderboard.
- **owning_doc:** `RESEARCH/CONTEXT.md`
- **owning_doc_updated:** N

### P4
- **invariant:** New experiment scripts MUST follow the `bench.py` shape: task list, fit/pred members, rolling_preds helper, pool blend, JSON+harness outputs; no hidden global state.
- **owning_doc:** `PROCESS/08_experiment/CONTEXT.md`
- **owning_doc_updated:** Y

## next_action_routing_changes
- Added experiment lightweight path concept to `PROCESS/WORKFLOW.md` stage routing.
- Added `PROCESS/08_experiment/CONTEXT.md` draft as the experiment-stage contract.
- Planned `brain/worker/.omp/extensions/ts-brain.ts` injection seam as opt-in only for `--cwd brain/worker`; main agent remains clean.
## open_risks
- Live OMP launch/injection proof is not yet available; ROOT's own AGENTS notes API-seam-only validation for extensions. The planned `test_ts_brain_injection.mjs` covers callback seam first; live runtime is deferred.
- `experiments/playground.py` may duplicate `projects/ts-diverse/bench.py` member code. Planned cutover: import `ts-diverse` members directly when path assumptions stabilize.
- Brain coverage remains scoped to h720/ts-ml per existing digest headers; broader graph coverage requires corpus rebuild.
