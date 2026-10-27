---
type: Concept
title: open_questions
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Open Questions — Idiotproof Workspace

Each records why it could not be resolved, not just that it was not.


## Q1. Is the 33–44% navigation-step reduction portable to a non-monorepo workspace?

The Formal Architecture Descriptors study (arXiv 2604.13108) measured coding agents in codebases. This
workspace is a knowledge/research pipeline, not a software project — the navigation is across stage
folders and a corpus, not source modules. The *mechanism* (explicit architectural context removes the
exploration phase) should transfer, but the magnitude may not.

**Why unresolved:** the study's setting is monorepo navigation; no comparable measurement exists for
document/knowledge workspaces. Would require instrumenting this workspace's own sessions to answer
empirically — possible, but out of scope for a literature scan.


## Q2. Where exactly is the 371-line AGENTS.md threshold for a stage contract, not a root file?

The 2,500-repository analysis found 371 lines (the `maas` repo) to be the empirical upper bound before
splitting becomes necessary. But that is a measurement of a *root* instruction file, and this workspace
distributes contracts across many stage folders.

**Why unresolved:** no study measures per-folder contract length. The single-disclosure-level rule (§4)
argues contracts should stay short, but "short" has no measured bound here. The honest position: 371 lines
is an upper bound for a *root* file; a stage contract should be well below it, but the number is
extrapolated, not sourced.


## Q3. Does Anthropic's 80% system-prompt deletion extend to knowledge-work contexts?

Anthropic removed 80%+ of Claude Code's system prompt for Claude Opus 5 / Fable 5 with no measurable loss
— **on their coding evaluations**. The finding is about *coding* guardrails (comment rules, docstring
rules, planning-document rules) that were compensating for limitations older models had.

**Why unresolved:** no equivalent measurement is published for research/knowledge/pipeline contexts. A
reflection-stage contract that forces chunk-id citations is arguably doing genuine verification work
(§6, total-function constraint), not compensating for a model weakness — but that is reasoning by
analogy, not evidence. **This is the highest-value question to answer empirically in this workspace**,
because it decides whether the current contract density is an asset or a liability for frontier models.


## Q4. Which of this workspace's current constraints are compensating for model limitations that no longer exist?

This is the actionable form of Q3, and it cannot be answered by literature at all — it requires
ablation. Candidates by suspicion level:

- **Likely still load-bearing:** chunk-id citation requirement (verification, not capability), INBOX-empty
  invariant, fingerprint/stamp provenance, deterministic tag routing.
- **Possibly obsolete:** verbose stage-contract prose describing what a folder does (§12: describe
  capabilities, not paths; models can list directories), repeated re-anchoring instructions, prescriptive
  output-format templates.

**Why unresolved:** needs an A/B run — same task, contract stripped to invariants only, compare gate
pass rate and output quality. Not run; recorded so the next session can pick it up.


## Q5. Do the ICM token budgets (2k–8k/stage) still hold for 2026 frontier models?

The ICM paper's per-stage budget of 2,000–8,000 tokens was measured for the model families available at
writing, and the paper itself flags this as an open question: *"does the five-layer hierarchy...
generalize across model families, or is it tuned to the specific attention patterns of the models
tested?... all current testing has been conducted on a single model family."*

**Why unresolved:** the paper scopes cross-model evaluation as future work. Combined with §7 (Anthropic
finding less context is now better), the budget may be conservative in the wrong direction — 2k–8k may
now be more than optimal, not less.


## Q6. Was the 0.91→0.64 hierarchical collapse reproducible, or a single-model artifact?

The progressive-disclosure study's most design-constraining number — hierarchical pack collapsing
multiple-choice accuracy from 0.91 to 0.64 — was observed on *one* Pi/model pairing ("one Pi/model
pairing sees multiple-choice accuracy collapse").

**Why unresolved:** the paper reports it as a sometimes-occurring failure, not a universal one ("never
helps and sometimes breaks accuracy outright"). The direction is clear (a second level does not help);
the *magnitude* is from a single configuration. The single-level rule is safe on the evidence; the
strength of "two levels is actively dangerous" is weaker than the headline implies.
