---
type: Concept
title: Plain-language comprehension meter and mechanism comparison
status: design
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Plain-language comprehension meter

## Research question
Which prompt-layer mechanism best improves reader comprehension of LLM summaries without reducing faithfulness: an always-on style rule, few-shot demonstrations, or post-hoc rewriting?

## Meter
The primary outcome is held-out lay-reader comprehension. For each source passage, generate question items from the source before any summary is scored. Each item has a known answer and tests either multiple-choice recognition or short-answer recall. Report item accuracy, exact-match recall, and a macro-average by passage. The question bank is never generated from the candidate summary.

A secondary proxy is an LLM rubric with fixed criteria: simplicity, informativeness, coherence, and faithfulness, each scored 1--5 with the same rubric and blinded candidate labels. It is used for iteration and diagnosis, not as the final winner criterion. FactPICO-style factuality checks are a safety counter-metric.

## Mechanism candidates

1. **Always-on style rule.** Add a fixed instruction before generation: use concrete words, explain unavoidable terms, one idea per sentence, preserve qualifiers and numbers, and do not omit decision-relevant facts.
2. **Few-shot.** Add two source-summary exemplars selected from the training/development set, demonstrating the same style rule and faithful simplification. No held-out passage or question appears in examples.
3. **Post-hoc rewrite.** Generate a normal summary, then apply a second pass with the style rule. The rewrite receives only the source and draft, and must preserve claims, numbers, uncertainty, and scope.

The control is the same model and source with no mechanism instruction. Temperature, token budget, source order, and evaluation prompts are held constant. Candidate labels are randomized for scoring.

## Evaluation protocol
Use a fixed development set for prompt tuning and a held-out test set for the final comparison. Stratify passages by length and domain. Produce one summary per condition per passage with a deterministic seed, then repeat on three seeds for stability. Generate at least 20 held-out passages and 5 comprehension items per passage: three multiple-choice and two recall items. A small lay-reader cast independently rates a blinded subset for understandable/not understandable and provides a free-text difficulty note; this is a validity spot check, not a replacement for the oracle-backed task.

Primary analysis is paired by passage and seed. Compare each mechanism with control using bootstrap confidence intervals over passage-level comprehension scores. Report the mean paired lift, 95% interval, recall and multiple-choice separately, and the fraction of passages improved. Report rubric scores and factuality failures separately. Do not use readability indices as a primary outcome.

## Verdict rule
Select the mechanism with the highest held-out comprehension score if its paired lift over control has a confidence interval excluding zero. If intervals overlap, prefer the simpler mechanism: always-on rule, then few-shot, then post-hoc rewrite. A candidate cannot win if factuality is lower than control beyond the pre-registered safety margin, or if it introduces any critical unsupported claim. G-Eval-style rubric results explain the outcome and guide follow-up, but cannot overturn the tier-1 result. Record all seeds, prompts, item banks, raw scores, exclusions, and failed safety checks.

## Harness entry point
The executable skeleton is `scripts/plain_language_meter.py`. Its contract is covered by `tests/test_plain_language_meter.py`; run `python -m pytest tests/test_plain_language_meter.py -q` before changing the scoring adapter.

## Limitations and manual check
The proxy rubric may disagree with lay readers, and source-derived questions can overrepresent explicitly stated facts. The acceptance check for this project is broader than a sentence-level proxy: run one realistic research task end to end through literature research, ingest, graph retrieval, reflection, and implementation of the resulting knowledge. The evidence must include the task question, source and ingest result, graph query and retrieved chunk IDs, reflection claims linked to sources, implementation diff or output, final verification result, and a human groundedness verdict. This is gate G3 and remains human-owned.
