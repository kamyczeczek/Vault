---
type: Concept
id: 2026-09-16_idiotproof-workspace-depth-breadth
date: 2026-09-16
scenario: S4
surface: agent+human workspace legibility, progressive disclosure, simplicity
status: done
supersedes: none
title: README
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Research: Idiotproof Workspace — Depth, Breadth, and the Walk Toward Simplicity

The question: how do you make a workspace that an **agent and a human** can both understand at **different
levels of depth and breadth** — a `CONTEXT.md` in every folder — while the whole thing keeps walking
*toward* simplicity rather than away from it?

This workspace is already an ICM (Interpretable Context Methodology) implementation, so the research was
scoped to what the literature says about that specific design axis, and — importantly — what evidence
exists that it *fails*.

**Headline finding:** the literature supports the layered-folder approach with real measurements, but the
strongest signal in the whole body of research points the **opposite** way from where most implementations
go. Anthropic **deleted over 80% of Claude Code's system prompt** for their newest models with *no
measurable loss* on coding evaluations. The frontier is moving toward *less* context, not better-organized
more. Full detail in `findings.md` §7.

**Second finding, and the one that constrains the design most:** depth is not free. The first controlled
study of progressive disclosure found a **second routing level never helps and sometimes breaks accuracy
outrageously** — one Pi/model pairing collapsed multiple-choice accuracy from **0.91 to 0.64**. One level is
enough. This workspace's "single disclosure level" rule is not a stylistic choice; it is the empirically
load-bearing constraint on the whole architecture.

## Route
Add/refresh this record's row in `RESEARCH/CONTEXT.md` §"Deterministic routing" in the same session that
creates the record.

## Status
- done — exit contract satisfied: every claim cited, open questions recorded with reasons.
