---
type: Concept
title: open_questions
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Open Questions — Self-Improving Workspace Framework Integration

<!-- Each question states what could not be resolved and WHY. -->

## 1. Research Backlog from Inspiration (Mapped to Workspace Realities)

1. **R1 (SkillOpt Mechanism vs Implementation):** What is the minimal bounded update size for prompt overlays and skills? Is character-budget truncation sufficient, or must semantic patch boundaries be enforced?
2. **R2 (CODESKILL Trajectory-to-Skill):** Can multi-step tool failure trajectories in `failure_ledger.jsonl` be automatically clustered into procedural skills using deterministic token graphs rather than LLM calls?
3. **R3 (SkillGLoW Procedural Families):** What is the optimal family granularity for this workspace? (Proposed: 4 high-level families vs 12 specific sub-families).
4. **R4 & R5 (Evidence Thresholds & Risk Weighting):** Should low-risk hints (e.g. tool parameter types) promote at $N=1$, while high-impact workflow rules (e.g. git hooks or AGENTS.md directives) require $N \ge 3$?
5. **R6 & R14 (Context Cost vs Retrieval):** When the prompt overlay scar digest grows, does selective FTS retrieval outperform static prompt injection, or does retrieval failure create silent recurrence blind spots?
6. **R7 (Skill Granularity):** What is the optimal shape for an invariant? (Current scars average 20–40 words; micro-heuristics vs comprehensive procedural playbooks).
7. **R8 (Add vs Rewrite vs Merge vs Delete):** Can discharged scars be deleted entirely from disk, or must they remain in `reflection_index.json` while being omitted only from the overlay digest?
8. **R9 (Negative Memory Noise):** Does maintaining a negative memory buffer prevent repetitive bad proposals, or does it consume retrieval budget with negative distractions?
9. **R10 (Decay):** How to handle time-based vs usage-based decay for rare but critical safety scars (e.g., git push/reset guardrails)?
10. **R11 (Causal Attribution):** When downstream task success improves after a workspace change, how do we distinguish genuine causal improvement from task difficulty variance?
11. **R12 & R13 (Interference & Composition):** How to detect when two separately valid procedural invariants create conflicting constraints when injected together?
12. **R15 & R16 (Learning from Success & Near-Misses):** How to harvest optimal trajectories from clean task executions, not solely from failure ledger errors?
13. **R17 (Consolidation Cadence):** Is per-session consolidation superior to multi-session / close-of-day sleep cycles?
14. **R18 (Harness Engineering):** How to improve preflight observability without adding latency to every tool call?
15. **R19–R25 (Contamination, Model/Harness Dependence, Human vs LLM, Trust Tiers):** Are our scars portable across models (e.g. Claude vs GPT-4o vs local models), or are they model-specific compensation mechanisms?

## 2. Open Workspace Integration Questions

16. **How to stage candidate heuristics without breaking the `verify_reflection_sync.py` pre-commit gate?**
    - The current sync gate strictly verifies that every schema-shaped markdown file under `MONITORING/reflection/` is indexed and seeded into memory.
    - If candidate heuristics live in `MONITORING/candidates/`, they must have a distinct parser and lifecycle so unvalidated candidates do not prematurely seed memory.
    - *Resolution path:* Isolate candidates under `MONITORING/candidates/` with their own extension/schema, completely separate from `MONITORING/reflection/`.

17. **How to perform held-out validation of prompt heuristics without external LLM evaluators?**
    - `inspiration.md` emphasizes validating changes against unseen tasks before promotion.
    - In this stateless, single-agent workspace, running a parallel LLM evaluation harness for every candidate heuristic is cost-prohibitive.
    - *Resolution path:* Divide heuristics into:
      (a) *Machinery/typed invariants:* Validated deterministically via differential python unit suites (like `tests/test_tool_preflight.py`).
      (b) *Behavioral/prompt heuristics:* Validated via frozen synthetic task prompt transcripts or held-out command execution logs.

18. **Backward compatibility of existing 48 reflections / 85 scars:**
    - The existing 48 reflection files do not have an explicit `family:` field in their markdown headers.
    - If `build_reflection_index.py` requires `family`, either all 48 files must be migrated or the indexer must heuristically infer the family from `owning_doc` and keywords.
    - *Resolution path:* The indexer should apply deterministic keyword/owning_doc mapping rules to classify legacy scars, while new reflections declare `family:` explicitly in frontmatter.

## 3. Remodeling-Plan Open Questions (2026-09-06)

19. **Candidate evidence threshold and authority:** What evidence must be
    mandatory for `accepted` versus `experimental` candidates, and who may
    promote each state? The plan proposes deterministic evidence fields but
    no local held-out behavioral corpus exists yet. *Resolution path:* C1
    defines the schema and checker first; C7 later supplies behavioral
    evaluation. Until then, only machinery candidates with executable red
    paths can be accepted automatically.

20. **Scar demotion window:** How many clean post-birth sessions or days are
    enough to demote a scar from static digest to index-only without hiding a
    rare safety constraint? The current EPI sample is short and includes
    near-miss noise. *Resolution path:* C4 uses conservative non-deleting
    experimental rendering, demands classified landed outcomes and retained
    `ask.py` retrieval, then validates against held-out trap recalls.

21. **Negative-memory consult noise:** Can a mandatory planning consult
    surface the relevant rejected proposal without producing distracting
    false warnings? Current `ask.py rejected` prints all four entries, while
    scored query matching is keyword-based. *Resolution path:* freeze five
    representative planning prompts, measure warnings, and only then make
    C2's routing row binding.

22. **Human-intervention outcome metric:** What explicit, privacy-preserving
    marker would reliably capture human correction or babysitting? There is
    no safe basis to retrospectively infer it from conversations. *Resolution
    path:* require a user-approved opt-in marker and trial it before using it
    in acceptance claims.
