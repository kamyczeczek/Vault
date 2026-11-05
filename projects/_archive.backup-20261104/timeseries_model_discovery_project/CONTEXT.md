---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# Time Series Model Discovery Workspace

Purpose: discover, benchmark, and select time-series forecasting models through a repeatable evidence-first pipeline. Outputs are ranked model candidates with validation evidence, not narratives.

## Current state

See `PROGRESS.md` for active slice, blockers, and next action.

## Routing

- Scenario intake → `PROCESS/WORKFLOW.md`
- Stage execution → `PROCESS/<stage>/CONTEXT.md`
- Knowledge queries → `brain/internal/ask.py`
- Core doctrine → `PRINCIPLES.md`
- Skills → `skills/SKILLS.md`

## Rules

- One disclosure level: root → stage folder → stage CONTEXT.md. No meta-routers.
- Always-loaded contract must stay under ~2k tokens.
- Every failure produces a structural change in the same session.
- Every "done" claim cites a re-runnable command with a log path.
