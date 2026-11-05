---
type: Concept
title: investigation
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Playbook: investigation

When to use: deep dive into complex workflows, mysterious behavior, or performance investigations.

## Steps

1. Map the request path / execution flow.
2. Gather git history, ADRs, or prior logs.
3. Formulate falsifiable hypotheses.
4. Test and document findings.

## Prove it works

Findings must cite the artifact they came from (file + line, query result, log excerpt) — never a claim without a pointer.
