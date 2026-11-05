---
type: Concept
title: workspace-organization-audit
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

fingerprint: 5f4f9d29057b  plan_version: ad0a031aa564 phase: 04_reflect
routing: ask.py --tag icm --tag interpretable-context --limit 12; ask.py --tag context-engineering --tag anti-leakage --limit 12; ask.py --tag icm --tag reflection --limit 8; ask.py --tag icm --tag determinism --limit 12
slug: workspace-organization-audit
method: in-process audit (omp agent spawn hangs at the harness level on both omp/18.1.4 and omp/18.2.0 — verified: `omp agent -p PING_OK` produced no output in 90s with no extension loaded; the audit contract was executed directly with the same deterministic routing the spawn contract mandates, and the outputs are validated by the same gate, `scripts/check_reflection.py`)

## Method

Routing used the exact tag-intersection contract the audit prompt specifies. One
of its three mandated queries is a dead route (see F4):

```
python knowledge/graph/ask.py --tag icm --tag agent-workspaces --limit 12   -> 0 chunks (DEAD ROUTE)
python knowledge/graph/ask.py --tag context-engineering --tag anti-leakage --limit 12
python knowledge/graph/ask.py --tag icm --tag reflection --limit 8
```

Substituted for the dead route (chosen from `knowledge/topics.md`, the
controlled vocabulary):
`icm + interpretable-context` (12 chunks), plus `icm + determinism` for the
hash-gate findings.

Chunk-id set used as the principle base (12 representative ids):
`00_interpretable_context_methodology_folder_structu`,
`00_icm_43_copies_four_moves`, `00_icm_knowledge_big`,
`00_is_progressive_disclosure_all_you_need_for_long`,
`00_from_plan_to_action_how_well_do_agents_follow_th`,
`00_awesome_context_engineering`, `00_adapt_as_needed_decomposition_and_planning_with`,
`00_agent_memory_hierarchies`, `00_progressive_disclosure_icm_depth_orthogonality`,
`00_memory_for_autonomous_llm_agents_mechanisms_eval`,
`00_enhancing_llm_based_agents_via_global`, `00_plans_don_t_persist_why_context_management_is_lo`.

Inspection was bounded: `ls`/`find -maxdepth 2` over both roots, plus the
loose root files, skills catalog, brain stores, and the project's own stage
contracts. No corpus bodies were read except via `ask.py`.

## Verdict

The project under audit (`projects/workspace-research`) is ICM-sound and
demonstrates the methodology's strongest property — its contracts are
machine-enforced and self-checking, so defects surface as failing gates rather
than silent drift. The containing workspace (`ROOT`) is materially weaker:
it holds two untracked experiment shadows that duplicate tracked work in a
project, its routing table advertises a root `skills/` directory that exists
only as a 3-file stub while the 42 real skill folders live in `.jcode/skills/`,
and one of this project's own stage contracts hardcodes a fingerprint three
corpus states stale. The defects are cosmetic-to-moderate, not structural: each
is a single file or directory move, and none has corrupted derived state
(all three project gates currently pass).

## Findings

| # | Observed evidence (path) | Principle violated/upheld (chunk id) | Change to make |
|---|---|---|---|
| 1 | `stages/04_reflect/CONTEXT.md` line "Determinism: hash-gated on `.graph_fingerprint` (fingerprint `35b86bc954fa` current)" — but `knowledge/graph/.graph_fingerprint` reads `0626262b2982`. The contract that documents the hash gate cites a fingerprint dead since the 2026-09-15 corpus tag repair. | violated `00_interpretable_context_methodology_folder_structu` (folder structure must be self-describing; a contract that mis-describes its own state is worse than no contract) | Delete the parenthetical hash from the contract prose: a hardcoded fingerprint is stale by construction as the corpus moves. Reference the fingerprint *file* only: "hash-gated on `.graph_fingerprint` (live value read from the file at gate time)". |
| 2 | `h720/` and `sub_experiments/` at ROOT are **untracked** (`git ls-files h720 sub_experiments` = 0) but NOT empty: `h720/sub_experiments/spectral_omega_gate/TSFM_SLICE_SPEC.md` is a real 53-line file, a **superseded revision** of the 62-line current spec in `projects/ts-ml-experiments/h720/sub_experiments/spectral_omega_gate/`. `sub_experiments/level_free_nonlinear_s35/` is an empty directory. The audit's original claim "0 git-tracked files ⇒ empty shells" conflated tracked-count with file-count. | violated `00_interpretable_context_methodology_folder_structu` (one home per artifact) + `00_from_plan_to_action_how_well_do_agents_follow_th` (untracked work is not persisted) | NOT "delete the shells". Do NOT delete: the root copy holds Phase-1 analysis absent from the current spec (guard-2 val→test shift `0.5194 ≥ 0.5` FAIL, 76.1% test windows in regime C vs 46.6% val, call rate 0.7608, `ρ(Ω,σ)=0.7975`), superseded when the project re-ran Phase 1 and the guard PASSED at `0.3832`. User's stated workspace policy preserves untracked WIP (`methods/__init__.py` ELMTree preserved 2026-09-03, `fnn_mi_elm_tree/` pending decision). Two safe options: (a) archive the superseded revision into the project dir as `TSFM_SLICE_SPEC_phase1_superseded.md` with a one-line pointer, or (b) leave in place and mark the root copy with a SUPERSEDED pointer header. Deletion is irreversible and loses the Phase-1 numbers. |
| 3 | Root `skills/` contains only `SKILLS.md`, `verify_catalog.py`, `mattpocock/` — but `skills/SKILLS.md` routes to 30+ skill names and `.jcode/skills/` contains 42 folders (agent-reach, code-review, domain-modeling, …). `AGENTS.md` row "Skills & Method Packages" documents `skills/` as the "physical home", with the true location in a parenthetical. | violated `00_icm_43_copies_four_moves` + `00_interpretable_context_methodology_folder_structu` (the routing table and the filesystem must agree; a table that points past its declared home is a broken contract) | Pick one and make the routing table say it: either make `skills/` the real directory (move `.jcode/skills/*` into it) or amend `AGENTS.md` §2 so `skills/` is documented as the catalog/router and `.jcode/skills/` as the physical home. The table must not imply a directory it does not contain. |
| 4 | `pipeline/06_reflect/_audit_workspace.prompt` mandates `ask.py --tag icm --tag agent-workspaces --limit 12` as its first routing query, but `agent-workspaces` is not in `knowledge/topics.md` (controlled vocabulary: context-engineering, icm, interpretable-context, agents, agentic, planning, memory, reflection, anti-leakage, prompt-engineering, progressive-disclosure, knowledge-graph, retrieval, determinism, evaluation, benchmark, self-evolution, world-models, decomposition, grilling, writing-for-agents, domain-modeling, context-md, glossary, routing, hooks, observability, classical-planning). | violated `00_icm_43_copies_four_moves` + `00_adapt_as_needed_decomposition_and_planning_with` (a plan is only executable if every step it names resolves; a dead route is an unexecutable step) | Change the query to a tag that exists — `icm + interpretable-context` returns 12 chunks covering the same principle set. Add a guard so this cannot recur: a prompt validator (or a line in `scripts/check_reflection.py`) asserting every `--tag` in a prompt's routing block appears in `knowledge/topics.md`. |
| 5 | 18 files in `MONITORING/reflection/` dated 2026-09-12..2026-09-14 are untracked (`??`), as are 6 in `RESEARCH/` and the new `brains/reflection_brain/reconcile_memory.py`. `AGENTS.md` Rule 6 makes the reflection file mandatory at work close; untracked work is written-but-uncommitted, so the invariant holds on disk but not in history. | upheld as designed `00_from_plan_to_action_how_well_do_agents_follow_th` (a plan that is not persisted cannot be followed across sessions) — the reflection files exist; they are simply not anchored in git | Commit the 25 untracked outputs in one bounded commit: `git add MONITORING/reflection/ RESEARCH/ brains/reflection_brain/reconcile_memory.py brains/ts_brain/corpus/06_ts_diverse_protocol.md` then verify with `git status --short`. This is a commit, not a restructure. |
| 6 | `problems/` at ROOT is an **empty directory** while `MONITORING/KNOWLEDGE/problems/` holds the live problem log, and `PROGRESS.md` "Open Problems" cites the `MONITORING/` path. Two problem homes, one unused. | violated `00_interpretable_context_methodology_folder_structu` (one home per concept) | Delete the empty root `problems/` (it has no files and no references in the routing table; `AGENTS.md` §2 routes problems to `MONITORING/KNOWLEDGE/problems/`). |
| 7 | `findings.md` at ROOT documents `chunk_knowledge.py` and describes writing to `brains/icm_brain/corpus/`, which now holds 123 chunks (97 naming `icm`). `brains/icm_brain/` and the project store both derive from the same ICM source — 123 chunks here vs 259 `icm_knowledge` chunks in `projects/workspace-research/knowledge/corpus/`. The same source is chunked twice into two stores with different ids. | violated `00_agent_memory_hierarchies` + `00_interpretable_context_methodology_folder_structu` (duplicate derivations of one source drift apart; the graph cannot know they describe the same content) | One store per source. `brains/icm_brain` is the ROOT-level brain the router serves; the project store is scoped to its own corpus — but if `ICM_knowledge.md` is chunked into both, make the project's copy a pointer (`icm` topic served by `brains/icm_brain` via `ask.py`) rather than a re-chunk. Lowest-risk alternative if a separate project store is desired: record the source file + sha in both manifests so the duplication is declared, not incidental. |
| 8 | Root `ask.py`, `build_brain.py`, `build_graph.py`, `chunk_knowledge.py`, `run_repomix.py` are brain-build/route scripts sitting at the ROOT top level beside `AGENTS.md`, while `AGENTS.md` §2 routes brain operations to `brains/` ("see `brains/CONTEXT.md` + `brains/brain_router.md`"). The scripts implement the documented contract but live outside the folder the contract names. | violated `00_interpretable_context_methodology_folder_structu` (scripts that implement a routed contract belong in that contract's folder) | Move the five scripts into `brains/` (`ask.py` stays a thin ROOT dispatcher if `brain_router.md` expects it at ROOT — in that case document it explicitly in `brains/CONTEXT.md` as "the ROOT entry point" rather than leaving it implicit). |

## Top 3 changes, ordered

**1. Do NOT delete the ROOT experiment shadows** (F2, corrected). The audit's
original recommendation (`rmdir h720 sub_experiments`) was based on a false
premise — it asserted the shells were empty on the evidence that `git ls-files`
returned nothing, but untracked ≠ empty. `h720/sub_experiments/spectral_omega_gate/TSFM_SLICE_SPEC.md`
is a superseded Phase-1 revision whose guard-2 failure numbers (0.5194, 76.1%
regime-C shift, call rate 0.7608) no longer exist in the current spec. Deleting
it would have destroyed a real artifact. The one-home violation stands, but the
remedy is to archive or mark it, and that choice belongs to the user — it is
untracked user WIP, and the workspace has an explicit precedent of preserving it
(`methods/__init__.py`, `fnn_mi_elm_tree/`).

**2. Remove the hardcoded fingerprint from `stages/04_reflect/CONTEXT.md`** (F1).
A contract that documents a live hash gate cannot itself pin a hash — the
pin is guaranteed stale. Replace the parenthetical with a pointer to the file:

```
- Determinism: hash-gated on `.graph_fingerprint` + `pipeline/WORKFLOW.md` sha12.
  `spawn.py` refuses if either missing/mismatched. (Live fingerprint is read
  from `knowledge/graph/.graph_fingerprint` at gate time, never hardcoded.)
```

Then re-stamp the 14 reflection outputs — editing `WORKFLOW.md`-adjacent
contract text does not change `plan_version` (the sha12 is over
`WORKFLOW.md` only), so the stamps stay valid; verify with
`python scripts/check_reflection.py`.

**3. Point the skills routing table at the real directory** (F3). Either move
the 42 skill folders from `.jcode/skills/` into `skills/`, or correct the
`AGENTS.md` §2 row to state the split explicitly. The second is cheaper and
reversible — amend the row's "Primary Reference / Tools" cell to read:
`skills/SKILLS.md` (catalog) + `.jcode/skills/` (physical home). Then run
`python skills/verify_catalog.py` to confirm the table still matches disk.

## Next bet

Fix F2, F1, F3 in that order (each is a bounded, reversible change verifiable
with an existing gate or a `git status` check), then close F4 by adding the
tag-vocabulary guard — a 6-line assertion in `check_reflection.py` that every
`--tag` appearing in a `pipeline/06_reflect/*.prompt` routing block exists in
`knowledge/topics.md`. That guard is what turns F4's one dead route from a
recurring silent failure into a failing gate, which is the pattern this
project has already applied four times to good effect (manifest gate,
reflection gate, watch gate, spawn timeout).
