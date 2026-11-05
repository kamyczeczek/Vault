---
type: Concept
title: feature
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Playbook: feature

When to use: implementing new functionality or capabilities.

## Steps

1. Define spec and acceptance criteria.
2. Design interfaces and components.
3. Write tests test-first (TDD loop).
4. Implement feature.
5. Verify end-to-end functionality.

## Prove it works

Acceptance criteria checked against the running artifact, not the diff; new tests green plus the surrounding suite green.
