---
type: Concept
title: bug-fix
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Playbook: bug-fix

When to use: fixing bugs, regressions, or failing tests.

## Steps

1. Build a tight, red-capable feedback loop (e.g. reproduction test with pytest).
2. Reproduce and minimise the failure.
3. Formulate ranked hypotheses.
4. Apply fix and add regression test.
5. Prove it works on the real artifact.

## Prove it works

Verification must match what changed (run the specific pytest command with `--basetemp .pytest_tmp`); never accept "build passed" or syntax checks as proof.
