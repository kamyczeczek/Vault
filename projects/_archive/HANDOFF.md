---
type: Concept
title: HANDOFF
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# HANDOFF — make every project an independent agent workspace (2026-09-28)

## Goal

User request: "use icm-architect to make every project able to be an
independent workspace where an agent can be run". Each `projects/<name>`
must let a cold agent (a) route from its own entry file and (b) know
exactly what is present/missing when it works without the full root
workspace.

## Decision (user-answered, do not re-ask)

Independence model = **Contract preflight**. Options offered:
hermetic vendoring, hermetic+remotes, contract preflight. User picked
contract preflight: sibling links stay live, no copies, one home per
fact (root rule D12 + ICM invariant 8). Each project gets a
`preflight.py` that self-diagnostics hard deps and external links.

## Facts gathered (ground truth, already verified by grep/ls)

- 6 active projects: `agentic-research-lab`, `benchmark-core`, `brain`,
  `etth1-h720`, `knowledge-retrieval`, `research-engine`. Plus
  `_archive` (exclude from all work).
- All are git repos; only `agentic-research-lab` has a remote.
  5 projects cannot be cloned standalone today.
- Cross-project touchpoints (from grep):
  - `etth1-h720/_workspace_paths.py` hardcodes
    `BENCHMARK_CORE = ROOT.parent / "benchmark-core"` and
    `ARCHIVED_DATA = ROOT.parent / "_archive/datasets"`; runs
    `bootstrap()` on import. Data file:
    `_archive/datasets/data/ETTh1_h1.csv` (exists).
  - `benchmark-core`: 3 scripts
    (`benchmark_multi_horizon.py`, `heuristic_hyperparameter_search.py`,
    `scripts/diebold_mariano_test.py`) do
    `sys.path.insert(0, HERE.parent/"_archive/datasets")` and import
    `fetch_scientific_datasets` (module exists). `bench.py` itself is
    standalone (downloads sunspots CSV, `data.py` absent is handled).
  - `research-engine`: `kg.py`, `query_*.py`, `check_tables.py` point
    at `../agentic-research-lab/knowledge/graph/graph.db`;
    `run_s47_suite.py` shells out to ARL's `build_graph.py`;
    `s47_ref/rolling_arm.py` does
    `sys.path.insert(0, ROOT/"benchmark-core/members")` and reads
    `ROOT/"_archive/datasets/data/ETTh1_h1.csv"`;
    `evict_stale_reflections.py` reads ARL `reflection/candidates/`;
    `sync_results_to_corpus.py` writes ARL `knowledge/corpus/`.
  - `knowledge-retrieval`: pure docs project (refs + reports), all
    measurement commands route into `../agentic-research-lab`
    (`knowledge/graph/run_retrieval_benchmark.py`, `ask.py`,
    `scripts/build_quarantine.py`,
    `subprojects/vera/benchmark/QUESTIONS.md`). `reports/` dir does
    not exist yet (CLAUDE.md promises it).
  - `agentic-research-lab`: gate Q0 in `scripts/quality_check.py`
    invokes `ROOT.parents[1]/scripts/check_workspace_integrity.py`
    (workspace root, outside this repo); skills are already vendored
    locally with `skills/MANIFEST.md` (OK).
  - `brain`: fully self-contained locally; only advisory sibling
    pointer to ARL's `bootstrap_project_brain.py`.
- `agentic-research-lab` has local `skills/` with MANIFEST (Q14 rule);
  root-level `AGENTS.md` is the L0 router.

## Completed (this session, uncommitted)

1. `projects/brain/preflight.py` — written.
2. `projects/benchmark-core/preflight.py` — written, then corrected:
   `results/results_s47.json` downgraded hard -> optional (file is
   actually absent on disk; it is a regenerated suite artifact, not a
   startup dependency — preflight itself caught that).
   Also note its CHECKS list has the optional entry sitting above the
   hard ones (harmless, cosmetic; normalize if you touch it).
3. Smoke-ran both: `python preflight.py` in brain and
   benchmark-core, both exit 0 / READY in the full tree.
4. Conventions fixed by the two written files:
   - `preflight.py` = stdlib only, project root. `ROOT = Path(__file__).resolve().parent`;
     `SIBLINGS = Path(os.environ.get("WORKSPACE_ROOT", ROOT.parent))`
     where `WORKSPACE_ROOT` points at the dir holding all siblings
     (i.e. `projects/`), NOT the workspace root.
   - Check tuples `(severity, path, why)`; print lines
     `[ok]`/`[MISSING] local|ext <path> (<why>)`; hard-missing =>
     exit 1, verdict NOT READY.
   - Path display: local paths relative to `ROOT`, external relative
     to `SIBLINGS`.
4. Open nit to fix while continuing: severity vocabulary drifted
   between the two written files — brain uses `hard`/`optional`,
   benchmark-core uses `hard`/`soft`. Pick ONE
   (`hard`/`optional`, brain's) and make all six preflights
   consistent. Only `hard` counts toward exit code.

## Remaining (concrete list, in order)

1. **Write 4 more preflights**, same shape as the two done:
   - `etth1-h720`: hard local = `CLAUDE.md`, `CONTEXT.md`,
     `_workspace_paths.py`, `members/h2k.py`, `members/sab_l.py`,
     `members/amr_24_168.py`; hard ext =
     `benchmark-core/members/big_dict_elm.py`,
     `benchmark-core/members/knn_feature_forecaster.py`,
     `_archive/datasets/data/ETTh1_h1.csv`
     (+ optional `_archive/datasets/fetch_etth1.py` as recovery step).
   - `research-engine`: hard local = `CLAUDE.md`, `CONTEXT.md`,
     `research_engine.py`, `mutation_engine.py`, `kg.py`; optional ext
     = ARL `knowledge/graph/graph.db` (query tools degrade), ARL
     `knowledge/graph/build_graph.py` (run_s47),
     `benchmark-core/members` (s47_ref arm),
     `_archive/datasets/data/ETTh1_h1.csv` (s47 ETTh1 task).
   - `knowledge-retrieval`: hard local = `CLAUDE.md`, `CONTEXT.md`,
     `references/defect-classes.md`, `references/measurements.md`;
     optional ext = ARL `knowledge/graph/run_retrieval_benchmark.py`,
     `knowledge/graph/ask.py`, `scripts/build_quarantine.py`,
     `subprojects/vera/benchmark/QUESTIONS.md`
     (every measurement command degrades without them).
   - `agentic-research-lab`: hard local = `CLAUDE.md`, `CONTEXT.md`,
     `skills/MANIFEST.md`, `scripts/quality_check.py`,
     `knowledge/graph/build_graph.py`; optional ext =
     `scripts/check_workspace_integrity.py` (gate Q0 fails fast only,
     all 18 project gates still run), `../../skills` (root shared
     factory — local `skills/` shadows it, so purely advisory).
2. **`etth1-h720/_workspace_paths.py`**: honor `WORKSPACE_ROOT` env
   (`SIBLINGS = Path(os.environ.get("WORKSPACE_ROOT", ROOT.parent))`
   instead of hardcoded `ROOT.parent`), keep default identical. Update
   its docstring. No other project uses the env yet, so only this
   file changes.
3. **`## Standalone` section in all 6 `CLAUDE.md`** (one short
   section each, ~5 lines): "run `python preflight.py` first; exit 1
   lists exactly what is missing; siblings live under
   `$WORKSPACE_ROOT` (default: `projects/` dir containing all
   projects); missing optional siblings degrade, missing hard blocks."
   Keep under the 60-line-ish budget per ICM invariant 2; these
   entry files already carry `Dependencies` sections — Standalone
   references them, does not duplicate.
4. **Root `AGENTS.md`**: add one rule: every project ships
   `preflight.py`; a session starting inside a project runs it first;
   `WORKSPACE_ROOT` env overrides sibling location. Then regenerate
   `MAP.md` via `python scripts/build_project_map.py`.
5. **Verify**: run all 6 `preflight.py` (expect 6x READY in full
   tree; then spot-check one project with
   `WORKSPACE_ROOT` pointed at a temp dir with only that project to
   confirm degradation report); run root gate
   `python scripts/check_workspace_integrity.py`; smoke one ARL gate
   chain if cheap (`python scripts/quality_check.py` in ARL).

## Repo state notes (pre-existing, NOT from this task)

- Root git: many modified/untracked files (`AGENTS.md`, `PHILOSOPHY.md`,
  `library/`, `skills/*`, etc.) from earlier sessions — uncommitted.
- ARL repo: `MAP.md` modified, `scripts/hook_post_tool.py` modified,
  untracked WAL/SHM files in `knowledge/graph/`.
- Do not commit anything this session unless told; handoff is the
  deliverable. New files this session: the two `preflight.py` above.

## Conventions / guardrails for the next agent

- ICM invariants in force: one folder one job, small stable entry
  files (CLAUDE.md stays routing-only; the new section points at
  preflight, does not inline the check list), one home per fact
  (never copy sibling code into a project for this task — the
  preflight records the link, it does not vendor).
- No invented abbreviations in new files; match doc style of existing
  `CLAUDE.md`s (they are prose + tables, no emoji).
- `AGENTS.md` answer-shape rule for chat: action first, numbered
  steps, one next step.
- Skill used: `skills/icm-architect` (Restructure mode, walk test).
  It is on disk but not registered in the skill system — read from
  path, not `skill://`.
