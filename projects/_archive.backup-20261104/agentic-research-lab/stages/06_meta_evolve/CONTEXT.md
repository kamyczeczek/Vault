---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Stage 06_meta_evolve — Feedback Loop & Workflow Evolution

Translates empirical findings and promoted research rules in `reflection/memory.md` into concrete updates for the research workflow, stage contracts, prompt templates, and audit gates.

## Inputs
- Promoted research rules in `reflection/memory.md`
- Active stage contracts (`stages/*/CONTEXT.md`)
- Pipeline specification (`pipeline/WORKFLOW.md`)

## Process
1. Inspect promoted operational rules in `reflection/memory.md`.
2. Determine if any rule prescribes a modification to:
   - Search methodology (e.g. multi-step query expansion in `stages/00_expand/`)
   - Synthesis protocol (e.g. structured citation tables in `stages/04_reflect/`)
   - Quality checks (e.g. new audit gate in `scripts/audit_workspace.py`)
3. Propose or apply the changes using `scripts/apply_meta_learning.py`.
4. Run workspace audit to ensure all modified contracts remain valid and compliant.

## Outputs
- Updated stage contracts or script configurations.
- Audit entry in `reflection/meta_evolution_log.jsonl`.

## Invoke
```bash
python scripts/apply_meta_learning.py [--dry-run]
```

## Contract
- **Non-destructive evolution:** Workflow updates must never bypass existing integrity gates or erase evidence history.
- **Traceability:** Every evolved rule must record the originating `memory.md` rule and chunk citation.
- **Audit pass:** All tests in `scripts/audit_workspace.py` must pass after any evolution step.


## Evolved Protocol Rule (Verified Self-Evolving Synthesis Constraints)
<!-- meta-evolved: Verified Self-Evolving Synthesis Constraints -->
- **Origin Evidence:** ``00_a_comprehensive_survey_of_self_evolving_ai_agent`, `00_severa_verified_synthesis_of_self_evolving_agent``
- **Requirement:** Self-evolving agent workflows must pair generative updates with explicit formal or environment-based verifiers prior to state commitment.

## Evolved Protocol Rule (Regression-Gated Meta-Learning)
<!-- meta-evolved: Regression-Gated Meta-Learning -->
- **Origin Evidence:** `00_skillopt`, `00_verified_self_evolving_agent`
- **Requirement:** Meta-learning edits MUST NOT apply unless they pass through a regression gate. `apply_meta_learning.py` MUST run `quality_check.py --json` before and after applying any rule. If any quality gate transitions from passing to failing, the entire meta-learning pass MUST abort and restore from backup. Ungated evolution collapsed performance from 55.4% → 2.6% in SkillOpt stress testing; gated evolution stayed flat at 57.0%. Baseline capture is a one-time setup via `python scripts/apply_meta_learning.py --save-baseline`. After a successful apply, baseline advances to the new passing state. Any proposed rule that would regress a gate is rejected, not patched or special-cased.
