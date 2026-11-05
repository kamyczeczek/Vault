---
type: Concept
title: refactor
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Playbook: refactor

When to use: restructuring code, improving architecture, or cleaning up technical debt.

## Steps

1. Establish baseline test coverage / existing behavior.
2. Design architectural changes.
3. Apply incremental transformations keeping tests green.
4. Verify clean architecture and passing test suite.

## Prove it works

Behavior baseline (tests) green before and after; no test deleted to make the suite pass.
