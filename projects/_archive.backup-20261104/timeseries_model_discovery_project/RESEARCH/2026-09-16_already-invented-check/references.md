---
type: Concept
title: references
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# References — Is This Already Built By Someone?

All fetched directly (primary sources). Method: Exa search via **agent-reach** for
discovery; direct URL fetch for reading. No secondary summaries used as evidence.

## R1 — Heretek-AI/Agent-Proof (compile/edit gate prior art)
- **URL:** https://github.com/Heretek-AI/Agent-Proof
- **Type:** tool, TypeScript, MIT, 1★, npm `@heretek-ai/agent-proof`
- **Read:** full README (380 lines) via GitHub fetch
- **Used for:** §1 — the 3-tier stage model, Stage 1 edit-time position (`<50ms` at
  `PostFileEdit`), Stage 2 hard git gate on staged blobs (`<2.0s`), LoopBreaker
  (`FAILURE_LOOP_HALT` at ≥3 identical failures), test/spec freezing, and the explicit
  thesis that prompt-based guardrails degrade under context saturation.
- **Caveat:** 1★, single-author org. Read for *architecture*, not adoption.

## R2 — AddyOsmani, "Self-Improving Coding Agents" (reflection-loop prior art)
- **URL:** https://addyosmani.com/blog/self-improving-agents/
- **Type:** long-form engineering write-up, published 2026-01-31
- **Read:** full text (309 lines)
- **Used for:** §2 — the correspondence table: `progress.txt`↔`PROGRESS.md`,
  `prd.json`↔`STATE.md`, AGENTS.md↔AGENTS.md, and the compound-learning philosophy
  ("each improvement makes future improvements easier", traced to
  `snarktank/compound-product`). Also the unmet warning that a memory file only helps
  if it is actually injected in future prompts — the exact failure of my promotion loop.
- **Caveat:** secondary for the *philosophy* (it quotes compound-product); primary for
  the described practice. Cited as practice evidence, not as research.

## R3 — ChangeGuard (class-3 detection prior art)
- **URL:** https://software-lab.org/publications/fse2025_ChangeGuard.pdf
- **Type:** peer-reviewed paper, Proc. ACM Softw. Eng. 2, FSE, Article FSE043 (July 2025)
- **Authors:** Gröninger, Souza, Pradel (University of Stuttgart)
- **Read:** first 223 of 319 pages-equivalent (abstract through RQ1 results + FP/FN analysis)
- **Used for:** §3 — pairwise learning-guided execution; precision 77.1% / recall
  69.5% on 224 manually-annotated changes; **regression-test recall 7.6%** (suites
  miss 92.4% of semantics-changing changes); changed-code coverage 27%→92%; the scrapy
  motivating example (a "simplify" refactor that silently changes behavior on one input).
- **Caveat:** read partially (RQ2–RQ5 not read); Python-only; needs a fine-tuned
  CodeT5 model, so too heavy for a commit gate.

## R4 — "Confident and Wrong: Silent Semantic Failures in Coding Agents"
- **URL:** https://arxiv.org/html/2603.25764
- **Type:** peer-reviewed paper, arXiv:2603.25764v3 [cs.SE], 21 Jun 2026
- **Author:** Aman Mehta (Snowflake AI Research)
- **Read:** §1–§9 + references (281 of 413 lines)
- **Used for:** §4 — silent semantic failure (SSF) dominates failure (80% Llama 4,
  68% GPT-5); **pre-edit guard interventions are null** (interpretation guard Claude
  65.2%→64.8%, GPT-5 44.4%→46.0%; test-anchored GPT-5 44.4%→44.0%), establishing that
  a whole class of pre-edit prompts cannot repair validity; action bias (60–90% of
  runs edit already-correct code instead of abstaining); test-free process signals
  (3-gram loop detection 100% recall/0% FP; trajectory length r=−0.26).
- **Caveat:** SWE-bench Verified Python only; the paper itself flags compiled
  languages as an open question (§8) because a compiler may catch over-confident
  edits — relevant, since my compile gate is exactly such a compiler-stage check.

## R5 — Dropped, not used as evidence
- **Nevo "Error-to-Rule Pipeline"** (https://nevo.systems/blogs/nevo-journal/error-to-rule-pipeline)
  — **HTTP 402 paywalled.** Dropped rather than substituted with a summary of it.
  Named in findings §2 only as the origin of the term "error-to-rule", which is
  independently described by R2.
- **dcostenco/prism-coder** (`docs/self-improving-agent.md`), **azena-ai/self-improving-loop**
  — surfaced in the same search but not read; R2 already covered the loop pattern and
  reading two more descriptions of the same archetype would add no evidence.
- **github / twitter / reddit** — agent-reach doctor reports `warn` (unauthenticated);
  deliberately not used. A prior-art audit does not need login-state platforms.
