---
type: Concept
id: 00_measured_pre_registered_gate_s44
title: "Measured Lesson — Pre-Registered Gates Are the Only Thing That Makes a Promotion Legitimate (h720 S-44) (part 1/2)"
source: "measured_pre_registered_gate_s44.md"
tags: [forecasting, gate-semantics, planning, pre-registration]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---
taxonomy: #pre-registration #gate-semantics #forecasting
# Measured Lesson — Pre-Registered Gates Are the Only Thing That Makes a Promotion Legitimate (h720 S-44)

## What was measured

The h720 benchmark promoted a new incumbent (S-44, blend full 1.9781 / RMSE 2.4613, displacing
S-26 at 1.9909 / 2.4710). The promotion was legitimate **because of a specific mechanism**, not
because the number was good.

The mechanism: the pool, protocol, seed, and every number were fixed **before** the design
document existed. S-44 then changed exactly one thing — which conditions BIND the promotion —
over that frozen evidence. A parity clause makes this enforceable: if the harness does not
reproduce the frozen numbers to 1e-4, the harness is wrong and nothing proceeds.

## The four binding conditions (all must hold)

| # | Condition | Value | Result |
|---|---|---|---|
| G1 | MAE_full ≤ 1.9859 (≥ 0.0050 gain vs S-26) | 1.978126 | PASS |
| G2 | MAE_full < 1.9909 (strictly beat incumbent) | 1.978126 | PASS |
| G3 | MAE_disjoint-4 ≤ 1.9696 (stability cap) | 1.863419 | PASS |
| G4 | Paired-bootstrap Δ CI upper < 0 | upper −0.006913 | PASS |

Δ = per-origin MAE(blend) − per-origin MAE(S-26 anchor), B = 2000, seed 0, resampling origins.

## What makes this non-obvious

The interesting property is **what was demoted**. Under S-44's declaration, the
singleton-capability screen (PatchTST singleton val 3.0267) and the train-val gap (0.179497)
became **non-binding diagnostics**: they are reported and cannot flip a PASS to a FAIL.

That is the direct repair of the S-43 defect (see `measured_gate_semantics_s43`), where the
same two checks fused into the acceptance chain produced a REJECT on a promotion-grade blend.
The demotion is not leniency — it is the correct placement of a claim. A statement about whether
a *member* can stand alone is not evidence about whether the *assembly* is better, so it must
not sit in the same `and` chain as the assembly's promotion gate.

Also enforced: **a blend win does not re-open the member family.** The family close stands
independently of the promotion outcome. Otherwise a single positive result would silently
reopen a closed frontier, undoing the negative-result discipline.

## The transferable rule

**The decision must be designed before the evidence exists.** Concretely, for any promotion or
acceptance decision:

1. **Declare the binding gate up front** — which condition decides, and what is demoted to a
   diagnostic that cannot flip the verdict.
2. **Freeze the pool and protocol first.** A pre-registration over evidence that does not exist
   yet is not a pre-registration; it is a plan to tune until it passes.
3. **Make the gate reproducible from the harness**, with a parity clause (reproduce frozen
   numbers to a tolerance, or nothing proceeds). This is what distinguishes "I changed my
   interpretation" from "I changed my data".
4. **State the resolution rule for disagreement**, including whether a positive can reopen
   something already closed.
