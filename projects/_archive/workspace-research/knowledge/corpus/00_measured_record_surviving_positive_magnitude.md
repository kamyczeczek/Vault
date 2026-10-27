---
type: Concept
id: 00_measured_record_surviving_positive_magnitude
title: "Measured Lesson — Record the Magnitude of the Surviving Positive, Not Only the Verdict (h720 S-43 P3) (part 1/2)"
source: "measured_record_surviving_positive_magnitude.md"
tags: [evaluation, negative-results, planning]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---
taxonomy: #negative-results #evaluation
# Measured Lesson — Record the Magnitude of the Surviving Positive, Not Only the Verdict (h720 S-43 P3)

## What was measured

A model family was closed on a singleton-capability screen while a **real, transferable
held-out gain** was present in the same experiment. That gain was recorded nowhere searchable.
A future reader asking "did attention on patch tokens do anything at all?" would find only the
word "REJECT".

## The numbers

The held-out precondition — the part of the protocol that decides whether selection found
anything real — passed on the legitimate selector:

| Quantity | Value |
|---|---|
| S-26 delta-ridge control (held-out val) | 2.522480 |
| Best fast subset on the same split | 2.502112 |
| **Held-out gain over control** | **+0.020368** (threshold > 0.005) |

The selection trace shows where the signal is. Iteration 3 selected
`[nlinear_L336_a1, nlinear_L336_a10, patchtst_P24_D32_2L]` (true 2.4936); iteration 6 added the
fourth member (true 2.4928). The attention member is in every improving subset — it carries
signal the two linear anchors do not span.

**So the family close rests entirely on the singleton screen (3.0267 > 2.90) and the
regularization gap (0.1795 > 0.15) — not on absence of signal.**

## Why this distinction is load-bearing

A verdict says a decision was made. It does not say what was learned. Two experiments can both
end in REJECT for opposite reasons: one because the approach carried no signal, one because the
component could not stand alone but improved the assembly. To a planner they look identical
until the magnitude is recorded.

The practical consequence is a cost trap. Without the recorded number, the cheapest-looking
re-open is "try another non-linear member" — which re-pays the 488 s harness run and the
family-close reasoning from scratch. With the number, the re-open question becomes precise:
*the member cannot stand alone, but the 3-member blend with it beats the control by +0.0204
on held-out val* — a different and much better-targeted question.

The original bet had a fused acceptance list where this distinction was invisible (see
`measured_gate_semantics_s43`). But the recording failure is independent of the gate failure:
even with a correct gate, a verdict-only record still loses the gain.

## The transferable rule

**Every negative result should record the magnitude of whatever positive it contained.**
Concretely, for a rejected experiment:

- Record the best signal found, with its number, even when the verdict is negative.
- Record **what was demonstrated**, stated separately from **what was decided**. "The blend
  promotes; the member does not stand alone" is two findings, not one.
- State the number a future proposal would need in order to avoid re-paying the experiment's
  cost — the control value, the best value, and the threshold.
