---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# RESEARCH/ — Research Record Library (ICM record-library form)

## Purpose
Persistent home for **standalone research** (S4 RESEARCH, `PROCESS/WORKFLOW.md`
§4): one folder per completed or in-progress research record, addressed by
position. Research is read-only by nature — it never edits code or plans;
implementation it uncovers re-enters the workflow as S1/S2.

## Structure
- `CONTEXT.md` — this file: the shelf contract + the deterministic routing
  table (the only routing surface for this shelf).
- `check_catalog.py` — fail-loud integrity gate (commit-time, S5-maintained).
  Mirrors the `skills/verify_catalog.py` pattern: the routing table is not
  trusted on declaration — it is checked before any commit that could touch
  the shelf (scar S-s12 P2: a routing surface without a verifier is a silent
  mis-router).
- `_template/` — factory for a new record (instantiate by copying, ICM
  invariant 10). The `_` prefix is the corpus boundary: `check_catalog.py`
  never treats `_`-prefixed entries as records (same boundary doctrine as
  the problem corpus — the template is NOT a live record).
- `<YYYY-MM-DD>_<slug>/` — one record per research. Fixed layout:
  - `findings.md` — every claim cited to a URL, file path, or local document.
    No unsourced claims.
  - `open_questions.md` — unanswered questions with the reason each could
    not be resolved (missing access, conflicting sources, out of scope).
  - `references.md` — flat list of every external source consulted
    (URL + access date + 1-line summary).
  - `README.md` — frontmatter (see below) + 3–8 line abstract + status.
  Records with `status: in-progress` are legal (the shelf is the state
  machine; a reopened record resumes inside its own folder).

### Record frontmatter (README.md, YAML `---` block at file top, gate-parsed)
```
---
id: <YYYY-MM-DD>_<slug>          # MUST equal the folder name
date: <YYYY-MM-DD>
scenario: S4                      # S4 standalone | S1 research-phase
surface: <one-line domain>
status: in-progress               # in-progress | done | superseded
supersedes: <id> | none
---
```

## Deterministic routing (no LLM — run this before any S4 work)
Given the research topic, apply the rows **in order**; the first match is
the route. `surface` in a table row is a set of lowercase tokens; a row
matches iff **at least 3 of its tokens appear (case-insensitive substring)
in the topic or the topic's domain**.

| # | Surface tokens | Record | Route when |
|---|---|---|---|
| R-01 | h720 ettth1 forecasting etth1 sota directions model experiment | 2026-09-02_h720-etth1-research | new work about the h720 ETTh1 forecasting surface: SOTA comparison, experiment directions, protocol facts |
| R-02 | knowledge architecture brain injection hooks context memory | 2026-09-03_knowledge-architecture-research | new work about agent knowledge architecture: inject-vs-query, multi-brain management, hook mechanism roles |
| R-03 | antifragile workspace stronger problems slop robust learning-from-failure scars reflection | 2026-09-05_antifragile-workspace-design | new work about making an agent workspace gain strength from problems / reduce slop over time: workspace-optimization, skills-as-memory, scars/reflection loops, kanban/atomic-agent patterns |
| R-04 | failure ledger epidemiology trap recurrence mechanizable preflight typed-interface scar-efficacy digest-budget merge | 2026-09-06_scar-efficacy-typed-interfaces | new work about MEASURING the workspace's failure signals: ledger classification, trap-class recurrence after scars, preflight/typed-interface hardening, digest merge-by-efficacy, epidemiology metrics. (Design-level antifragile questions route R-03; measurement/efficacy questions route here. If both match, HALT per Rule 4.) |
| R-05 | self-improving evolving substrate candidate validation procedural family negative-memory compilation | 2026-09-06_self-improving-workspace-framework | new work about self-improving workspace architecture: evolving substrate, candidate heuristics, procedural families, validation gates, negative memory buffer, and SkillOpt/SkillGLoW/CODESKILL compilation |
| R-06 | agent writing activity files workspace setup continuity scratchpad state handoff | 2026-09-07_agent-activity-file-logging-workspace-setup | new work about agents writing what they do into files / workspace setup: scratchpads, state/handoff docs, contract-vs-state splits, memory-file posture |
| R-07 | graph brain code knowledge project whole codebase call import community hotspot blast dead | 2026-09-11_graph-brain-project-knowledge | new work about a graph brain that knows the whole project in detail and enables extremely fast problem/architecture surfacing and next-direction recommendation: tree-sitter indexing, call/import graphs, communities, LSP, BM25+vector+RRF, GNN/code-graph RAG |
| R-08 | idiotproof workspace legibility depth breadth simplicity context.md folder progressive-disclosure navigation convention | 2026-09-16_idiotproof-workspace-depth-breadth | new work about making a workspace legible to BOTH agent and human at different depth/breadth: CONTEXT.md per folder, progressive disclosure vs RAG, navigation as dominant agent failure, convention-over-configuration, worse-is-better simplicity, and the counter-evidence that frontier models improve with LESS context. (Self-improving/measurement questions route R-04/R-05; this row is the workspace-shape-as-interface surface.) |
| R-09 | software factory spec slop chaotic mapping persistence compaction babysitter orchestrator aiming tuning verification | 2026-09-16_software-factory-slop-persistence | new work about the agentic SOFTWARE FACTORY as a spec→software mapping: the aiming problem (landing in the tiny desirable-output subset), slop as the complement, chaotic/non-deterministic mapping, agent persistence designs (new-session tool / compaction / invisible babysitter), and tuning levers (instruction-document library, verification agents). (Workspace-shape/legibility questions route R-08; workspace failure-measurement questions route R-04.) |
| R-10 | prior-art audit already invented reinvented gate loop self-improvement delta | 2026-09-16_already-invented-check | new work asking whether this workspace's self-improvement machinery is already built elsewhere: pre-commit/edit-time compile gates (Agent-Proof), reflection→memory compound loops (AGENTS.md/compound-product), silent semantic edit breakage and its detection (ChangeGuard, arXiv 2603.25764), and the one un-invented delta = measuring loop efficacy / trap recurrence. (Self-improving design questions route R-05; failure-measurement/efficacy questions route R-04; this row is the has-someone-already-built-this audit surface.) |
| R-11 | project workspace design instructions modular deterministic antifragile simple hierarchical recoverable state learning failure scar budget | 2026-09-18_project-workspace-design | new work asking for detailed instructions to build good project workspaces: modularity, simplicity, hierarchy, determinism, recoverable state, learning from failure, scar-lifetime budget, and concrete invariant lists. (Self-improving design questions route R-05; failure-measurement/efficacy questions route R-04; workspace-shape/legibility questions route R-08; this row is the instruction-shaped synthesis surface.) |
**Route outcomes (exact):**
1. **Match + record `done`** → REOPEN: edit inside the existing record
   folder (append findings, update open_questions, flip `status:
   in-progress`), then close back to `done`. One research = one folder,
   forever.
2. **Match + record `superseded`** → create a NEW record
   `<YYYY-MM-DD>_<new-slug>` whose README carries `supersedes: <id>`;
   update the superseded record's status if not already set.
3. **No match** → NEW: `copy _template/ → <YYYY-MM-DD>_<slug>/`, fill
   frontmatter, **add a row to the routing table above in the same
   session** (a record without a routing row is unreachable — scar
   S-00-skills-subsystem P1).
4. **Ambiguous (2+ rows match, neither clearly the topic)** → HALT, ask the
   user (Rule 4). Never guess.

## Gate contract — `check_catalog.py` (fail-loud, exit 1 on any violation)
1. **Record shape** — every non-`_` subfolder is a record: folder name
   matches `^\d{4}-\d{2}-\d{2}_[a-z0-9]+(-[a-z0-9]+)*$`, all three canonical
   artifacts exist non-empty, README carries all five frontmatter keys,
   `id` equals the folder name, `status` ∈ {in-progress, done, superseded}.
2. **Table ↔ disk** — every routing-table row's record column names an
   existing record folder; every `done`/`superseded` record appears in at
   least one row (coverage: an unrouted finished record is a silent routing
   hole).
3. **Supersede links** — `supersedes` targets exist and are not `none`-
   misformatted; no cycle.
4. **Live referrers** (informational, printed not fatal): scans tracked
   text files outside `RESEARCH/` for `PROCESS/02_research/(findings|open_questions|references)\.md` mentions and lists the live ones so a
   referrer drift surfaces in the commit log.

## Close sequence (S4, from WORKFLOW.md §6)
1. Artifacts complete inside the record folder (the three canonical files).
2. `findings.md` every claim cited; `references.md` every source
   (URL + date + 1-liner).
3. Add/refresh the routing-table row (route 1 or 3 above).
4. PROGRESS.md milestone + Next Action; Close per WORKFLOW.md §6.
5. `python RESEARCH/check_catalog.py` green (the pre-commit gate also runs
   it whenever `RESEARCH/` or the gate itself is staged).

## Forbidden in this shelf
- Code, configs, or plan edits (research is read-only; S1/S2 owns
  implementation).
- Hand-editing `check_catalog.py`'s parsed table shape without a
  red-path-validated test (gate-shape scar S-s20-validation-round4 P1:
  a gate is a gate only if it exits nonzero on violation AND has been
  proven to trip on an injected defect).
- Leaving a finished record out of the routing table.

## History
- 2026-09-05: shelf created (S5 work, user directive: standalone research
  needs its own folder + per-research subfolders + deterministic routing).
  Cutover from `PROCESS/02_research/` shared artifacts: the two historical
  commissions (2026-09-02 h720 ETTh1, 2026-09-03 knowledge architecture)
  were split out of the shared stage files into per-record folders in the
  same commit (scar S-h720-methods-consolidation P2: a move is a cutover —
  old and new tree never coexist as two homes).
