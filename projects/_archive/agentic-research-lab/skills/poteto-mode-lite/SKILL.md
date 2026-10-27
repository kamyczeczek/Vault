---
type: Concept
name: poteto-mode-lite
description: Minimal pstack-inspired workflow skill. Task to playbook routing for investigation, bug-fix, feature, and refactor, plus prove-it-works verification. Adapted for python/pytest and PowerShell.
disable-model-invocation: true
title: SKILL
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Poteto Mode Lite

A lightweight, pstack-inspired workflow orchestration skill adapted for Python (`pytest`, `python`) and PowerShell execution environments.

## Core Rules

1. **Understand before changing**: Inspect code, trace flow, and check history/context before proposing edits.
2. **Design before coding**: Define data structures, interfaces, and module boundaries before writing implementation code.
3. **Prove it works**: Verification must match what changed (e.g. running specific pytest commands with `--basetemp .pytest_tmp`), never accept "build passed" or syntax checks as proof.

## Playbooks (4 Playbooks)

### 1. investigation
> Full checklist: `playbooks/investigation.md`.
- **When to use**: Deep dive into complex workflows, mysterious behavior, or performance investigations.
- **Steps**:
  1. Map the request path / execution flow.
  2. Gather git history, ADRs, or prior logs.
  3. Formulate falsifiable hypotheses.
  4. Test and document findings.

### 2. bug-fix
> Full checklist: `playbooks/bug-fix.md`.
- **When to use**: Fixing bugs, regressions, or failing tests.
- **Steps**:
  1. Build a tight, red-capable feedback loop (e.g., reproduction test with pytest).
  2. Reproduce and minimise the failure.
  3. Formulate ranked hypotheses.
  4. Apply fix and add regression test.
  5. Prove it works on the real artifact.

### 3. feature
> Full checklist: `playbooks/feature.md`.
- **When to use**: Implementing new functionality or capabilities.
- **Steps**:
  1. Define spec and acceptance criteria.
  2. Design interfaces and components.
  3. Write tests test-first (TDD loop).
  4. Implement feature.
  5. Verify end-to-end functionality.

### 4. refactor
> Full checklist: `playbooks/refactor.md`.
- **When to use**: Restructuring code, improving architecture, or cleaning up technical debt.
- **Steps**:
  1. Establish baseline test coverage / existing behavior.
  2. Design architectural changes.
  3. Apply incremental transformations keeping tests green.
  4. Verify clean architecture and passing test suite.
