---
type: Concept
title: ecc_integration_reflection
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# ECC as Experimental Workspace for VERA — Reflection & Integration Design

**Date:** 2026-09-25
**Context:** VERA Phase 2 (simplicity/understandability + graph DB merge) complete; Phase 3 (DB-1) adopted; Phase 4 (E-suite injection) complete; Phase 5 (synthesis) pending
**Graph Fingerprint:** 44172cafee34 (10,364 nodes, 1,247,343 edges)

---

## Executive Summary

The ECC (Engineering Competency Catalog) repository at https://github.com/affaan-m/ecc is **not just a skill library** — it is a **production-grade experimental platform** for agentic evaluation, benchmarking, and harness construction. Its architecture directly mirrors VERA's research pillars:

| VERA Research Pillar | ECC Skill Mapping | Integration Value |
|---------------------|-------------------|-------------------|
| **Simplicity/understandability → performance** | `agent-harness-construction`, `context-budget`, `agentic-engineering` | Action-space minimalism, observation design, context budgeting as measurable levers |
| **Graph DB as unified workflow substrate** | `knowledge-ops`, `context-budget`, `unified-memory` | Corpus ↔ gateway ↔ ask.py as single read path (DB-1 validated) |
| **Claim-level eval (not doc-level)** | `agent-eval`, `eval-harness`, `benchmark-methodology` | YAML task definitions, pass@k metrics, tension plots → claim-scorecard isomorphism |
| **Verification gates as first-class** | `verification-loop`, `delivery-gate`, `gateguard` | Phase-gated verification mirrors VERA's G0-G3 + tier-dependent policy |
| **Causal falsification / negative controls** | `benchmark-methodology`, `eval-harness` (regression evals) | D1-D5 injection test ≡ ECC's capability + regression eval duality |
| **Cold-start understandability (SIM-2)** | `codebase-onboarding`, `context-budget`, `agent-harness-construction` | Orientation pack design = context budget + action space + observation format |

**Recommendation:** Use ECC as the **experimental workspace** for VERA Phase 5+ by:
1. **Cloning ECC locally** as a subproject (`subprojects/ecc/`) — not as dependency, as *workspace*
2. **Porting VERA's experiment harness** into ECC's `eval-harness` + `benchmark-methodology` framework
3. **Running VERA experiments as ECC eval tasks** with pass@k, cost, time, consistency metrics
4. **Using ECC's skills as independent variables** in simplicity ablations (SIM-1/SIM-2)

---

## Deep Capability Mapping

### 1. `eval-harness` — VERA's Experiment Runner Replacement

**Current VERA:** Custom Python scripts (`db1_parity_row.py`, `collect_clean_pools.py`, `plant_defects.py`, `gate_c.py`, `score_b01.py`)

**ECC `eval-harness` provides:**
- **YAML task definitions** — declarative, versioned, reproducible
- **Git worktree isolation** — each run gets clean repo state (solves VERA's "fresh session" requirement for SIM-2)
- **pass@k metrics** — pass@1, pass@3, pass^3 for reliability measurement
- **Three grader types** — code (deterministic), model (LLM-as-judge), human (adjudication) → maps to VERA's gate-C (auto) + D4 two-rater (human)
- **Capsule/receipt system** — hash-linked journal with integrity checks ≡ VERA's fingerprint provenance
- **Retrospective grouping** — aggregate verified capsules by task family ≡ VERA's synthesis report

**Integration design:**
```yaml
# .claude/evals/vera-sim1-simplicity.yaml
name: vera-sim1-simplicity-ablation
description: SIM-1 simplicity ablation S0 vs S1 vs S2 on VERA benchmark questions
repo: ./subprojects/vera
commit: "44172cafee34"  # VERA graph fingerprint as baseline pin
tasks:
  - name: S0-full-protocol
    prompt: |
      Run full VERA protocol (retrieve→answer→gate G0→G3) on Q1-Q23
      Use context_gateway.py with budget=default, fingerprint=44172cafee34
    judge:
      - type: code
        command: python scripts/score_claims.py --protocol S0 --questions Q1-Q23
      - type: model
        prompt: "Evaluate claim quality: grounding, reproducibility, negative controls"
    metrics: [pass_rate, cost, time, consistency, token_usage]
  - name: S1-retrieve-answer-gate1
    prompt: |
      Run S1 protocol (retrieve→answer→gate G1 only) on Q1-Q23
    judge:
      - type: code
        command: python scripts/score_claims.py --protocol S1 --questions Q1-Q23
    metrics: [pass_rate, cost, time, consistency, token_usage]
  - name: S2-no-gate
    prompt: |
      Run S2 protocol (retrieve→answer, no gate) on Q1-Q23
    judge:
      - type: code
        command: python scripts/score_claims.py --protocol S2 --questions Q1-Q23
    metrics: [pass_rate, cost, time, consistency, token_usage]
success_metrics:
  capability:
    pass@3: 0.90
  regression:
    pass^3: 1.00
```

### 2. `benchmark-methodology` — VERA's Claim Scorecard as Competitor Profiling

**Current VERA:** `claim_schema.md` + `score_b01.py` + `scorecard` gates

**ECC `benchmark-methodology` provides:**
- **9 weighted dimensions with 1-5 rubrics** → map to VERA claim dimensions (grounding, reproducibility, mechanism, limitation, confidence, etc.)
- **Tension plot** — two axes scored separately, never averaged → **exactly** VERA's tier-dependent gate policy (S1 for L1-L2, S0 for L3-L5)
- **Evidence-anchored scoring** — every score needs source link → VERA's `source_ids` + `verification_status`
- **Competitor profile card** → VERA's per-question per-protocol result card

**Integration design:**
```markdown
## VERA Claim Profile Card (maps to ECC competitor profile card)

### Q5 — "How does the lab's reflection protocol handle session compaction?"
- **Protocol / Tier:** S0 / L2
- **One-liner:** Full protocol with G0-G3 gates
- **Model / fingerprint:** B0.2-pinned / 44172cafee34
- **Notable sources:** 00_okf_methodology_research, 01_reflection_protocol.md

### Dimension scores (VERA claim rubric)
| Dimension | Score (1-5) | Justification | Source |
|---|---|---|---|
| Grounding (direct citation) | 5 | All claims cite corpus chunks via ask.py | claim.source_ids |
| Reproducibility (rerun parity) | 4 | r1=r2 for 22/23 claims | gate G2 log |
| Mechanism specificity | 4 | Explicit "reflection accepted rule candidates" | claim.mechanism |
| Limitation honesty | 3 | Notes context window pressure | claim.limitation |
| Confidence calibration | 4 | High/med/low matches human rater 87% | verification_status |
| Negative control survival | 5 | 0/5 D1-D5 defects undetected | injection test |

### Tension plot (VERA tier-dependent policy)
- **Simplicity (S1 sufficient?):** 4 — S1 achieves parity on L1-L2
- **Load-bearing (S0 required?):** 5 — S0 essential for L3-L5 causal claims
- **Quadrant:** high-simplicity / high-load-bearing → **VERA's validated policy**
```

### 3. `agent-harness-construction` — SIM-2 Cold-Start Understandability as Action Space Design

**Current VERA:** SIM-2 pack A (43.9 KB) vs pack B (1.7 KB, 96% smaller) — orientation packs for fresh sessions

**ECC `agent-harness-construction` provides:**
- **Action space quality** — stable, explicit tool names, narrow schemas
- **Observation quality** — status, summary, next_actions, artifacts
- **Error recovery contract** — root cause hint, safe retry, explicit stop
- **Context budgeting** — system prompt minimal, large guidance in skills on-demand
- **Granularity rules** — micro/medium/macro tools by risk/cost

**SIM-2 as harness construction experiment:**
```markdown
## SIM-2 Re-framed as Harness Construction

### Pack A (43.9 KB) — "Bloated Harness"
- System prompt: Full VERA protocol + all gate definitions + benchmark questions + schema
- Tools: ask.py, context_gateway.py, score_b01.py, gate_c.py, inject_defects.py (all exposed)
- Observation: Raw corpus chunks + full gate logs + injection positions
- Context: ~15K tokens before first tool call

### Pack B (1.7 KB) — "Minimal Harness"
- System prompt: "You are a research agent. Use context_gateway for retrieval. Cite sources. Run gate_c.py to verify."
- Tools: context_gateway.py (single entry point), gate_c.py (verification)
- Observation: {status, summary, next_actions, artifacts} — structured, not raw
- Context: ~400 tokens before first tool call

### Hypothesis (from agent-harness-construction principles):
Pack B achieves ≥ Pack A quality on L1-L2 (simpler action space, better observation design)
Pack B achieves ≤ Pack A quality on L3-L5 (insufficient recovery contract for causal reasoning)
```

### 4. `context-budget` — Token Economics as Performance Driver

**Current VERA:** DB-1 gateway saves ~35-45% tokens via per-kind reservation; B0.2 pinning reduces query fan-out

**ECC `context-budget` provides:**
- Phase 1: Inventory all components (agents, skills, rules, MCP, CLAUDE.md)
- Phase 2: Classify (always/sometimes/rarely needed)
- Phase 3: Detect issues (bloat, redundancy, MCP over-subscription)
- Phase 4: Report with ranked optimizations

**VERA integration:** Run `context-budget` on VERA workspace to quantify:
- Token cost of S0 vs S1 vs S2 protocols
- Token cost of gateway (D1) vs free crawl (D0)
- Token cost of pack A vs pack B orientation
- **Optimization target:** Minimize tokens while maintaining claim quality (Pareto frontier)

### 5. `verification-loop` / `delivery-gate` / `gateguard` — VERA's Gates as ECC Verification Phases

**Mapping:**
| VERA Gate | ECC Verification Phase |
|---|---|
| G0 (no verification) | Skip verification-loop |
| G1 (grounding gate) | Phase 1 (Build) + Phase 2 (Type Check) — does claim compile against corpus? |
| G2 (reproducibility rerun) | Phase 4 (Test Suite) — pass^3 = 100% for regression |
| G3 (negative controls) | Phase 5 (Security Scan) — injection test D1-D5 detection |
| Tier-dependent policy | `gateguard`: "parallel-batch siblings may already be applied" — conditional gate application |

---

## Experimental Workspace Architecture

```
agentic-research-lab/
├── subprojects/
│   ├── vera/                    # Current VERA (keep as research corpus)
│   │   ├── benchmark/
│   │   ├── experiments/
│   │   └── ...
│   └── ecc/                     # CLONED ECC repo — experimental workspace
│       ├── skills/
│       │   ├── eval-harness/    # ← VERA experiment runner
│       │   ├── benchmark-methodology/  # ← VERA claim scorecard
│       │   ├── agent-harness-construction/  # ← SIM-2 harness design
│       │   ├── context-budget/  # ← Token economics measurement
│       │   ├── verification-loop/  # ← VERA gates as phases
│       │   ├── agent-eval/      # ← Agent comparison (future: compare VERA protocols)
│       │   └── benchmark/       # ← Performance baselines
│       ├── agents/              # VERA-specific agents (researcher, verifier, synthesizer)
│       ├── evals/               # VERA experiment definitions (YAML)
│       │   ├── vera-sim1.yaml
│       │   ├── vera-sim2.yaml
│       │   ├── vera-db1.yaml
│       │   ├── vera-injection.yaml
│       │   └── vera-synthesis.yaml
│       ├── scripts/
│       │   └── lib/eval-harness/  # Capsule, replay, receipt utilities
│       └── .claude/
│           └── evals/           # Eval definitions + run history
```

---

## Pilot Experiment: VERA-ECC Integration (Phase 5 Entry)

### Experiment: "ECC Harness Runs VERA SIM-1"

**Objective:** Validate that ECC's `eval-harness` can execute VERA's SIM-1 simplicity ablation with:
- Git worktree isolation (fresh session per arm)
- pass@k metrics (reliability, not just mean)
- Capsule receipts (provenance = VERA fingerprint)
- Retrospective grouping (synthesis report automation)

**Design:**
```yaml
# ecc/.claude/evals/vera-sim1.yaml
name: vera-sim1-simplicity-ablation
description: Replicate VERA SIM-1 using ECC eval-harness
repo: ../vera
commit: "44172cafee34"
runs_per_task: 3  # pass@3 measurement
tasks:
  - name: S0-full-protocol
    prompt_file: prompts/sim1_s0.md
    judge:
      - type: code
        command: python ../vera/scripts/score_claims.py --protocol S0
      - type: model
        prompt_file: prompts/claim_quality_grader.md
  - name: S1-retrieve-answer-gate1
    prompt_file: prompts/sim1_s1.md
    judge:
      - type: code
        command: python ../vera/scripts/score_claims.py --protocol S1
      - type: model
        prompt_file: prompts/claim_quality_grader.md
  - name: S2-no-gate
    prompt_file: prompts/sim1_s2.md
    judge:
      - type: code
        command: python ../vera/scripts/score_claims.py --protocol S2
      - type: model
        prompt_file: prompts/claim_quality_grader.md
success_metrics:
  capability:
    pass@3: 0.80  # S0/S1 target; S2 expected lower
  regression:
    pass^3: 1.00  # All arms must be deterministic at claim level
```

**Execution:**
```bash
cd subprojects/ecc
# 1. Define eval
/eval define vera-sim1

# 2. Run (creates git worktrees, executes agents, grades)
/eval run vera-sim1 --agent claude-code --runs 3

# 3. Report (generates pass@k, cost, time, consistency table)
/eval report vera-sim1 --format table

# 4. Retrospective (groups verified capsules for synthesis)
node scripts/eval-harness.js capsule group vera-sim1
```

**Expected outcome:**
- Replicates VERA SIM-1 verdict (S1 ≥ S0 quality AND ≤0.5× cost for L1-L2)
- Adds **reliability dimension** (pass@3, consistency) missing from current VERA
- Produces **capsule receipts** for each run → hash-linked provenance
- Generates **synthesis-ready retrospective** for Phase 5 report

---

## Strategic Value: Why ECC as Workspace (Not Just Reference)

### 1. **Dogfooding the Platform You're Studying**
VERA studies "agentic research mechanisms." ECC *is* an agentic engineering platform. Running VERA experiments *inside* ECC's eval harness creates a **recursive validation loop**: the platform evaluates its own design principles.

### 2. **Standardized Experiment Interface**
Current VERA: 8 custom Python scripts with ad-hoc CLI.
ECC eval-harness: YAML tasks → `agent-eval run` → standardized report → capsule receipt.
**Benefit:** Future experiments (Experiment A query decomposition, Experiment C verification routing) become *new YAML files*, not new Python scripts.

### 3. **Agent Comparison Infrastructure**
`agent-eval` skill compares Claude Code, Aider, Codex, etc. on same tasks.
**VERA application:** Compare "VERA protocol as agent" vs "baseline agent" vs "simplified agent" — with pass@k, cost, time metrics. This *is* Experiment A/C/E but with rigorous methodology.

### 4. **Skill as Independent Variable**
ECC skills are modular, versioned, loadable on-demand.
**VERA application:** SIM-1/SIM-2/DB-1 ablations become *skill activation patterns*:
- S0 = load `verification-loop` + `delivery-gate` + `gateguard`
- S1 = load `verification-loop` (Phase 1-2 only)
- S2 = load no verification skills
- Pack A = load all VERA skills
- Pack B = load only `context-gateway` + `gate-c` skills
- D0 = load `ask.py` skill (free crawl)
- D1 = load `context-gateway` skill (budget-aware)

### 5. **Provenance Chain: Fingerprint → Capsule → Receipt → Retrospective**
VERA fingerprint (44172cafee34) → ECC capsule (hash-linked journal) → ECC receipt (offline verification) → ECC retrospective (grouped synthesis).
This **closes the loop** from VERA's "claim-level provenance" to "experiment-level provenance."

---

## Implementation Roadmap

### Week 1: Workspace Setup
- [ ] Clone ECC to `subprojects/ecc/`
- [ ] Verify `eval-harness` utilities run (`node scripts/eval-harness.js example`)
- [ ] Create VERA-specific agents in `ecc/agents/` (researcher, verifier, synthesizer)
- [ ] Port VERA benchmark questions to ECC eval YAML format

### Week 2: Pilot Experiment (SIM-1 Replication)
- [ ] Write `vera-sim1.yaml` with 3 tasks (S0, S1, S2)
- [ ] Write prompt files and judge configs
- [ ] Run `/eval run vera-sim1 --agent claude-code --runs 3`
- [ ] Compare results with existing `subprojects/vera/experiments/runs/SIM1_arms.md`

### Week 3: SIM-2 as Harness Construction
- [ ] Write `vera-sim2.yaml` with pack A/B as harness configs
- [ ] Use `agent-harness-construction` principles to design pack C (optimized)
- [ ] Run cold-start evaluation in fresh git worktrees (ECC handles isolation)

### Week 4: DB-1 + Injection as Regression Evals
- [ ] Write `vera-db1.yaml` (D0 vs D1 parity)
- [ ] Write `vera-injection.yaml` (D1-D5 detection as capability evals)
- [ ] Run regression evals on every gateway/ask.py change

### Week 5: Synthesis & Meta-Evolution (Phase 5)
- [ ] Use `eval-harness` retrospective to auto-generate synthesis report
- [ ] Apply `benchmark-methodology` tension plot to VERA promotion candidates
- [ ] Run `apply_meta_learning --dry-run` via ECC's `continuous-learning-v2` skill

---

## Risk Assessment & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| ECC eval-harness too immature for VERA complexity | Medium | High | Pilot SIM-1 first; fallback to current scripts if capsule system fails |
| Git worktree isolation breaks VERA's corpus dependency | Low | Medium | Pin commit to VERA fingerprint; corpus is in same repo |
| ECC skills require Node.js (eval-harness uses Node) | Low | Low | `node scripts/eval-harness.js` works; Python agents called via subprocess |
| Context budget overflow in ECC workspace | Medium | Medium | Run `/context-budget` first; lazy-load VERA skills only when needed |
| Learning curve for ECC conventions | Medium | Low | Start with `eval-harness` only; adopt other skills incrementally |

---

## Conclusion

**ECC is the ideal experimental workspace for VERA's next phase.** It provides:
1. **Rigorous experiment methodology** (eval-harness, benchmark-methodology) replacing ad-hoc scripts
2. **Harness construction principles** (agent-harness-construction) formalizing SIM-2's intuition
3. **Context economics** (context-budget) quantifying VERA's token/performance tradeoffs
4. **Verification as first-class** (verification-loop, gateguard) mirroring VERA's gate architecture
5. **Agent comparison infrastructure** (agent-eval) for Experiment A/C/E
6. **Provenance chain** (capsule → receipt → retrospective) extending VERA's fingerprint model

**Next action:** Clone ECC, run pilot SIM-1 replication. If successful, migrate all VERA experiments to ECC eval-harness framework for Phase 5 synthesis and beyond.