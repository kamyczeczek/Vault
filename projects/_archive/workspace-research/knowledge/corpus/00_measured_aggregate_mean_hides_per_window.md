---
type: Concept
id: 00_measured_aggregate_mean_hides_per_window
title: "Measured Lesson — A Regression Hidden by the Mean Was Measured Against the Wrong Baseline (h720 S-43 P2) (part 1/2)"
source: "measured_aggregate_mean_hides_per_window.md"
tags: [evaluation, forecasting, stale-baseline]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---
taxonomy: #evaluation #stale-baseline #forecasting
# Measured Lesson — A Regression Hidden by the Mean Was Measured Against the Wrong Baseline (h720 S-43 P2)

## What was measured

A candidate improved the aggregate mean (−0.0128) while regressing on the hardest window
(+0.0470). The per-window regression was **real but invisible in every headline number**, and
the one place it was surfaced was compared against a **stale baseline** rather than the
incumbent actually being defended.

## The numbers

| Metric | Value | Direction |
|---|---|---|
| `test_full` (2161-origin mean MAE) | 1.978126 | −0.0128 vs S-26 (better) |
| `test_disjoint` | 1.863419 | −0.1062 vs S-26 (better) |
| `test_w4` (hardest window, spring 2018) | 1.889616 | **+0.0470 (worse)** |

The +0.0470 regression existed **only against a hardcoded constant** (`S26_W4 = 1.8427`,
copied from the S-20 6-member leaderboard row). Against the in-harness S-26 anchor — the
incumbent actually being defended — the same window is **−0.0683 (better)**:

```
s26_incumbent_w4: 1.9579365851264652
s20_reference_w4: 1.8427
w4_delta_vs_s26:  -0.06832021007558842
```

Both numbers were in the harness log. The acceptance path silently used the stale constant.

## Two distinct defects, one artifact

**1. The mean hides per-window harm.** W4 is the documented hardest window for every model
since S-01. A 2161-origin mean over heterogeneity averages away exactly the regime where the
model fails. An aggregate gain is compatible with — and in this case coexists with — a real
degradation in the hardest regime. **A mean is not evidence of uniform improvement.**

**2. The baseline was not the defended incumbent.** The per-window comparison used a constant
copied from an older leaderboard row (S-20, 6 members) instead of the S-26 2-member anchor
being defended. The comparison was arithmetically correct and semantically wrong: it answered
"better than S-20?" while the decision was "better than S-26?".

The harness logged both numbers, so the truth was available. The acceptance path used the
wrong one. **Availability of the correct value is not the same as using it.**

## Root causes

- The W4 reference was copied from a leaderboard row rather than taken from the incumbent the
  experiment was actually run against. No mechanism asserted "the baseline in the comparison
  is the baseline in the acceptance gate".
- No per-window condition existed alongside the aggregate one, so a per-window regression was
  structurally uncatchable by the gate — it could only be noticed by a human reading a log.

## The transferable rule

**Every comparison in an acceptance gate must name the incumbent it compares against, and that
name must be the same in the comparison, the gate, and the log.** Concretely:
