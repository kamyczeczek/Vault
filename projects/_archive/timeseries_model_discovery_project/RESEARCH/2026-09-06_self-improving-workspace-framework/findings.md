---
type: Concept
title: findings
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Findings — Self-Improving Workspace Framework Integration

## 1. Core Thesis & Grounded Mapping

The framework in `inspiration.md` ("Self-Improving Workspace") posits that an AI agent's workspace serves as an external, evolving substrate for a frozen model. Improving performance over time requires compiling raw execution experiences into validated, bounded procedural skills, rather than accumulating uncurated episodic memories.

Mapping the framework's 35 principles to the current Windows/Jcode workspace reveals strong foundations already built, alongside key architectural gaps:

| Framework Principle | Current Workspace State | Status & Bridge |
| :--- | :--- | :--- |
| **Phase 1: Experience Capture (§1, §3)** | `failure_ledger.jsonl` + `dispositions.jsonl` + transcript joins | **Implemented.** Captures 100% of tool failures, near-misses, and dispositions with mandatory pre-commit gating. |
| **Active Preflight Gates (§7, §12)** | `.jcode/hooks/tool_preflight.py` (P1–P5) | **Implemented.** Blocks known failure modes (edit anchors, multiline `-c`, run-before-write, robocopy, read schema) pre-execution. |
| **Failure Epidemiology (§26, §28)** | `.jcode/hooks/epidemiology.py` (`EPI` metric) | **Implemented.** Measures live entries, mechanizable share, extinct classes, and recurrence post-gate birth daily. |
| **Procedural Families (§8, §9)** | `classify_family()` in `build_reflection_index.py`; `family` on all 87 scars; `ask.py families` / `list --family`; asserted by `tests/test_procedural_families.py` | **RESOLVED (Phase 1, 2026-09-06 D2).** All 87 scars classified into the 4 families (repo-hygiene 30, knowledge-routing 30, protocol-domain 18, tool-interaction 9); legacy scars via deterministic keyword/owning_doc matching, new reflections may declare `family:` explicitly. Digest grouping by family remains Phase 2+. |
| **Candidate Buffer & Gate (§5, §13)** | `candidates.jsonl` (empty, staging surface); reflections still commit directly to index | **PARTIAL.** Staging file + `ask.py candidates` reader exist, but candidates have no lifecycle/parser yet (open question 16): validation-gated promotion is still manual. |
| **Negative Memory (§16)** | `brains/reflection_brain/rejected_candidates.jsonl` (4 entries, C-001..C-004); `ask.py rejected`; AVOID warnings on scored queries | **RESOLVED (Phase 2 partial, 2026-09-06 D2).** Queryable negative memory live: known-bad proposals with refutation reasons, seeded from solved problems; never injected into the overlay digest. |
| **Workspace Subtraction (§17, §18)** | Stable truncation in `gen_digest.py` (1855 tok) | **Gap.** No systematic pruning or merging of discharged scars whose classes are verified extinct by the epidemiology probe. |
| **Sleep / Consolidation (§23)** | Ad-hoc session closes | **Gap.** No structured consolidation routine to cluster recent failures and compress invariants. |

## 2. Deep Dive on Architectural Components

### A. Experience vs. Skill & Procedural Families (SkillGLoW / CODESKILL)
- **Principle:** Experience is an episodic log of a specific task failure; a skill is a generalized, actionable procedure (`WHEN <trigger> DO <action> BECAUSE <failure_mode> VERIFY WITH <test>`).
- **Workspace Diagnosis:** Our reflection corpus currently atomizes scars at an individual session level (e.g., 5 separate scars on git CRLF/submodule/hook interactions, 6 on repomix pack composition). This causes the prompt overlay scar digest to balloon (currently 1,855 tokens, ~50% of the entire overlay budget).
- **Consolidation Target:** Group scars into **Procedural Families**:
  1. `tool-interaction`: edit anchoring, bash quoting, python script execution, read schemas.
  2. `git-and-repo-hygiene`: branch anchoring, clean state, CRLF churn guard, selective staging.
  3. `protocol-and-domain`: TS-ML evaluation splits, time-series horizons, registry immutability.
  4. `knowledge-and-routing`: ICM shelf traversal, brain rebuild synchronization, deterministic table gates.

### B. Two-Tier Lifecycle: Candidates & Validation Gate (SkillOpt)
- **Principle:** No heuristic is automatically promoted to the active prompt overlay upon first observation ($N=1$). A proposed rule is merely a hypothesis (`candidate`), which must survive a validation gate before promotion.
- **Validation Mechanics for Coding Workspaces:**
  1. *Tool & Machinery Rules:* Must be backed by executable differential tests with proven red-path failures (identical to our 14 red-path proofs in `test_tool_preflight.py` and 3 in `test_epidemiology.py`).
  2. *Workflow & Routing Rules:* Must pass deterministic integrity verifiers (`check_workflow.py`, `check_catalog.py`, `verify_catalog.py`).
  3. *Prompt Invariants:* Evaluated against held-out regression cases to verify they do not produce false-positive restrictions or prompt dilution.

### C. Negative Memory Buffer
- **Principle:** Storing rejected heuristics with explicit refutation evidence prevents the agent from falling into repetitive loops of proposing previously failed ideas.
- **Implementation:** Introduce `MONITORING/rejected_candidates.jsonl` (schema: `id`, `proposed_rule`, `failure_mode`, `refutation_evidence`, `family`). During planning (S3) or reflection (T1–T5), `brains/reflection_brain/ask.py` queries both active scars and rejected candidates.

### D. Subtraction by Measured Efficacy (D2 Merge Doctrine)
- **Principle:** A self-improving workspace must be able to `ADD`, `REVISE`, `MERGE`, `DEPRECATE`, and `DELETE`.
- **Criterion (Grounded in R-04 & D3):** Use the daily `EPI` metric from `epidemiology.py`:
  - If a failure class is verified **extinct** post-birth (e.g., `robocopy=0`, `read-schema=0`), its corresponding scars in the prompt overlay digest can be demoted to index-only (retrievable on demand via `ask.py`, but omitted from the static prompt overlay).
  - If a class continues to recur, its heuristic must be rewritten into a typed preflight gate (`tool_preflight.py`), not an informational prompt scar.

## 3. Phased Implementation Roadmap

1. **Phase 1: Procedural Family Taxonomy & Index Schema (S5, D2 Milestone)** — DONE 2026-09-06
   - Update `build_reflection_index.py` to classify scars into procedural families. ✓ `classify_family()`, `family` field on all 87 scars, `families` summary block, `ask.py families`/`--family`, `tests/test_procedural_families.py` (10/10).
   - Update `gen_digest.py` to group digest entries by family and filter out discharged/extinct classes, bringing overlay token cost from 1,855 down to <1,000 tokens. ✗ PENDING (digest still flat/newest-first at 1,895 tok; grouping + extinct-class demotion needs the EPI signal wired into gen_digest).

2. **Phase 2: Candidate Staging & Negative Memory Buffer (S5)** — PARTIAL 2026-09-06
   - Negative memory buffer live at `brains/reflection_brain/rejected_candidates.jsonl` (4 entries) with `ask.py rejected` + query-time AVOID warnings. ✓
   - Candidate staging surface live at `candidates.jsonl` + `ask.py candidates` reader, but `MONITORING/candidates/` with its own parser/lifecycle is NOT built (open question 16). ✗ PENDING
   - Update `ask.py` to surface negative memory when evaluating proposed modifications. ✓

3. **Phase 3: Formal Consolidation / Sleep Cycle in WORKFLOW.md (S7/S5)**
   - Add a deterministic Consolidation Stage to `PROCESS/WORKFLOW.md`:
     `EPI probe -> Failure clustering -> Candidate extraction -> Differential test validation -> Digest pruning`.

## 4. Addendum — Idiotproofing Remodeling Plan (2026-09-06)

### A. Decision and evidence boundary

The newly ingested `sources/workspace-remodeling-guide.md` correctly sets a
safety boundary: inspect → research → plan → human review → implement →
validate, rather than immediately rewriting the workspace. This addendum is
therefore **a plan, not authorization for the changes it lists**.

The relevant external evidence supports the boundary but does not prove that
any one proposed local change will improve this workspace:

| Evidence | What it establishes | Local implication | Confidence |
|---|---|---|---|
| Agentic Harness Engineering (AHE), arXiv:2604.25850 | File-level component observability, layered experience distillation, and edit-level predictions make harness updates reversible and falsifiable; reported 69.7→77.0% Terminal-Bench-2 pass@1 over 10 iterations, with cross-family transfer | We already have the first two pillars (versioned files, ledger/reflection/digest) but lack a structured candidate record that binds **prediction → validation evidence → promotion/rejection** | B: peer-reviewed-style preprint result, external workload
| Microsoft SkillOpt primary report | Bounded add/delete/replace edits, a held-out validation gate, best-version selection, and rejected-edit memory prevent prompt/skill drift; only 1–4 edits accepted in its case studies | Do not promote a candidate from one incident to an overlay scar. Give it a bounded lifecycle and a deterministic acceptance/rollback rule | B: vendor primary report, benchmark evidence not local evidence
| HarnessEvolve, arXiv:2609.00829 | Separating execution, evaluation, optimization, and gating is meant to reduce credit-assignment error, shortcut learning, and forgetting; updates must protect recent work and pass held-out validation | Keep executor, evidence recorder, candidate proposer, verifier, and commit gate conceptually separate even when one agent performs them serially | C: recent preprint, no local replication
| Engineering Reliable Coding Agents, arXiv:2608.13867 | Reliability is system-level: task construction, execution state, retrieval, memory, verification, permissions, and observability can each invalidate conclusions | Root-cause taxonomy must not default to “add an instruction” or “model error”; it must route to the owning harness layer | B/C: broad structured review, applicability must be measured locally

### B. Current workspace map (observed, not aspirational)

| Component | Purpose / state | Owner / verifier | Idiotproofing strength and remaining weakness |
|---|---|---|---|
| `AGENTS.md` + `PROCESS/WORKFLOW.md` | authoritative routing, S1–S7 classifier, stage sequence, knowledge queries | deterministic `check_workflow.py` | Strong routing and fail-loud ambiguity policy. Weakness: negative memory is documented but not yet a mandatory planning consult.
| `.jcode/hooks/tool_preflight.py` | blocks five measured tool-composition traps before execution | 31-check suite, 14 red paths, live hook | Strongest structural layer. Its scope is intentionally narrow; new rules need incidence and false-positive evidence.
| `.jcode/hooks/failure_ledger.py` + transcript harvest | captures observer and shell failures and blocks commits with OPEN entries | 29-check suite, checkpointed runtime store | Strong observability. Current ledger mixes raw failures, near-misses, and self-validation noise, so promotions must use typed classification rather than gross counts.
| `.jcode/hooks/epidemiology.py` | measures live failures, mechanizable share, gated recurrences, extinct classes, digest token cost | 25-check suite, 3 red paths | Provides the correct efficacy signal. It is daily and aggregate, not yet a candidate-level decision record.
| `MONITORING/reflection/` + reflection brain | turns solved work into indexed scars, memory cards, and static digest | parser, sync verifier, memory byte checks | Strong learning trace. It currently auto-promotes valid reflections, so unvalidated behavioral heuristics can still enter the static digest.
| `brains/reflection_brain/{candidates,rejected_candidates}.jsonl` | staging and negative memory | readers only | Candidate file exists but is empty and lacks schema/lifecycle/gate; negative buffer is queryable but not guaranteed at planning entry.
| `skills/`, skills_brain, overlay | catalog, routing signal, bounded auto-loaded skill descriptions | catalog/sync gates | Strong source/index/signal separation. Context cost is measured only for scar digest, not the whole always-loaded instruction surface.
| Git + pre-commit + pack probes | reversible history, selective staging, integrity checks, pack freshness/composition | hook, pack2, pack3 | Strong recovery and evidence. No one command produces a compact “workspace health” baseline spanning all routine reliability signals.

### C. Friction map and root-cause classification

The map is grounded in the current contracts, the first EPI measurement, and
known scars. It deliberately separates observed friction from hypotheses.

| Rank | Observed friction / evidence | Root class | Why instructions are the wrong first response | Preferred intervention | Evidence needed before promotion |
|---|---|---|---|---|---|
| P0-1 | Candidate staging exists but has no lifecycle; behavioral rules may become active scars immediately (`findings` §1, current `candidates.jsonl` empty) | verification / learning lifecycle | More “be careful” prose cannot establish whether a new heuristic improves future work | **STRUCTURE + CHECK**: candidate schema and deterministic lifecycle with promotion gate | Candidate fixture tests: invalid state/schema rejected; no candidate appears in index/digest/memory; accepted candidate requires linked evidence and rollback field |
| P0-2 | Negative memory only surfaces by explicit `ask.py` call or keyword match (D2 scar P2) | retrieval / workflow | Knowledge sitting in a buffer does not prevent a proposal if the proposal choke point never reads it | **WORKFLOW**: mandatory rejected-candidate query at S1/S2/S3 planning and S5 redesign entry | `check_workflow.py` proves a live row and an automated test freezes an avoided proposal hit; measure query false-positive burden for 5 planning tasks |
| P0-3 | Static scar digest is 1,935 tokens and still flat/newest-first; EPI reports extinct classes but digest cannot demote them | context / subtraction | Adding more digest prose worsens the diagnosed condition | **STRUCTURE + CHECK**: family-grouped digest with explicit active/index-only state, demotion driven by a conservative EPI criterion | Baseline/current token count; retrieval test for demoted scar; red path rejects demotion without required evidence; held-out task checks no recurrence |
| P1-1 | EPI is aggregate daily output, not a proposal ledger with numerator, denominator, prediction, and outcome per intervention | observability / attribution | Narrative claims can over-credit a recent change | **TOOL**: append-only “change experiment” record linked to candidate, baseline window, expected effect, validation window, outcome, rollback | Fixture validates exact schema; a candidate cannot be promoted without a record; re-run emits same verdict from frozen inputs |
| P1-2 | Existing checks are individually strong but health is distributed over several commands; a reconnecting agent can choose an incomplete sweep | discoverability / workflow | A larger AGENTS checklist is more context burden | **TOOL**: read-only `workspace_health.py` that composes existing gates and reports per-layer PASS/FAIL/SKIP without hiding exit codes | Differential test uses injected stale index/open ledger/stale pack fixtures; real run does not mutate state; command is listed in routing docs only after red-path proof |
| P1-3 | EPI includes self-validation/near-misses and post-birth recurrences can be preflight blocks, so gross recurrence is not a direct measure of landed harm | measurement / attribution | “More gates” could make the ledger look worse while making execution safer | **CHECK / METRIC**: distinguish prevented, landed, and probe-induced incidents in candidate evaluation | Frozen raw rows classify into all three; report every numerator with basis; gate blocks are never claimed as landed recurrence |
| P2-1 | No held-out behavioral regression corpus for prompt/overlay candidate changes (R-05 Q17) | evaluation | Self-assessment is not independent evidence | **EXPERIMENT**: small frozen task-prompt/command-log corpus, partitioned development vs holdout | First prove corpus produces different outcomes for a deliberately bad rule vs baseline; only then use for promotion |
| P2-2 | No measured whole-overlay/context budget or instruction overlap audit | context / observability | Token count alone does not establish correctness cost | **RESEARCH + TOOL**: inventory stable prompt surfaces, deduplicate concepts, measure cost and task retrieval impact | Baseline report, no automatic deletion; compare candidates on defined task set before any reduction |
| P2-3 | Human corrections/intervention are an explicit north-star but not currently counted as a reliable metric | outcome measurement | Inferring corrections from arbitrary chat text would be noisy and privacy-sensitive | **HUMAN CHECKPOINT + optional explicit marker** | User-approved marker semantics, no retroactive inference, opt-in trial and false-positive review |

### D. Ordered remodeling plan

#### Horizon 0: do first, low-risk and reversible

1. **C1 — Candidate lifecycle contract.** Create a new S1/S5 slice that
   replaces the empty JSONL convention with a small, versioned schema:
   `id`, `state` (`proposed|experimental|accepted|rejected|deprecated`),
   `family`, `problem_evidence`, `proposed_change`, `prediction`,
   `validation`, `rollback`, `owner`, `created_at`, `updated_at`.
   Candidates remain outside reflection parsing, memory seeding, and the
   overlay. A deterministic checker rejects malformed entries and an
   acceptance transition without evidence. **Success:** all fixture
   transitions obey the state machine and no unaccepted candidate enters
   active channels. **Rollback:** delete the new isolated surface and its
   routing row, preserving rejected history in a migration record.

2. **C2 — Planning-time negative-memory consult.** Add a deterministic
   workflow knowledge row for S1/S2/S3/S5 plan or redesign entry that calls
   `ask.py rejected`; make the row's query live-gated. **Success:** five
   frozen planning prompts include the relevant rejected proposal and the
   consult emits its AVOID record, without unrelated warnings. **Rollback:**
   remove the row, keeping the buffer available on demand. This addresses D2
   scar P2 directly.

3. **C3 — Decision-record wrapper for a workspace change.** Before any
   future gate, workflow, or overlay edit, require one append-only candidate
   experiment record with baseline, expected effect, cost, evidence window,
   acceptance threshold, and rollback command. **Success:** a checker
   refuses promotion without all fields and exact linked validation evidence.
   **Rollback:** the record schema is additive and does not affect current
   machinery.

#### Horizon 1: only after Horizon 0 is green

4. **C4 — Scar subtraction experiment.** Implement family-grouped rendering
   as an *experimental* digest mode. Do not delete scars. Demote only when a
   class has a documented, conservative zero-landed-recurrence window after
   its gate birth, a retrieval path (`ask.py`) remains, and a red-path test
   proves missing evidence blocks demotion. Compare whole-digest tokens and
   a held-out trap-recall set. **Acceptance:** lower static tokens with no
   missed held-out required scar. **Rollback:** render the prior all-active
   index state from a committed snapshot.

5. **C5 — Read-only health dashboard.** Compose existing deterministic
   gates into one command, preserving each underlying command's output and
   nonzero result. It must report freshness, catalog, workflow, problem
   lifecycle, ledger state, EPI basis, and pack freshness separately.
   **Acceptance:** injected stale/open examples fail at the named layer;
   healthy real run is idempotent. It must not become another source of
   truth or hide gate failures.

6. **C6 — Incident outcome taxonomy.** Extend EPI or a sibling report only
   after fixture evidence can classify `prevented`, `landed`, and
   `self-validation` without guessing. Use it to judge C1–C5, not to claim
   a global reliability rate. **Acceptance:** all metrics state their
   baseline/live denominator and category definitions.

#### Horizon 2: research, not implementation authorization

7. **C7 — Held-out behavioral evaluation corpus.** Build only after the
   candidate lifecycle is live. Use synthetic, non-secret task prompts and
   command trajectories divided before optimization. The corpus should test
   false positives, retrieval failures, and instruction bloat, not merely
   successful wording imitation.

8. **C8 — Consolidation cadence experiment.** Compare per-session versus
   close-of-day clustering with predeclared workload, cost, and regression
   metrics. Do not automate promotion or deletion from a single run.

9. **C9 — Human-intervention metric.** Propose an explicit opt-in marker
   after user review. Never mine private conversation text retrospectively
   as a proxy for corrections.

### E. Explicit non-changes

- Do **not** rewrite `AGENTS.md`, add generic instructions, or create more
  skills as the first response. The primary sources and local EPI evidence
  favor structural/check/tool interventions over prose.
- Do **not** build an autonomous workspace optimizer, self-modifying loop,
  or automatic scar deletion. The relevant research explicitly relies on
  separated roles and evaluation gates; this workspace has no behavioral
  holdout corpus yet.
- Do **not** equate a low EPI count with reliability. The ledger contains
  baseline history, near-misses, and probe noise; all rates must state basis
  and category.
- Do **not** change Jcode hook assumptions. The active harness has observers
  plus `pre_tool`, but no prompt-time injection channel.
- Do **not** touch user-owned WIP (`build_brain.py`, h720 FNN tree,
  `methods/__init__.py`, legacy reflection WIP) as part of remodeling.

### F. Decision requested

The recommended next implementation is **C1 + C2 as one bounded S5/S1
program**, but only after the user approves the plan. It has the clearest
local evidence, does not alter existing execution semantics, and creates the
evaluation boundary required before any higher-risk self-improvement.
