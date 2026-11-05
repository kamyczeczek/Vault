---
type: Concept
id: 2026-09-03_knowledge-architecture-research
date: 2026-09-03
scenario: S4
surface: agent knowledge architecture, brain injection, hooks
status: done
supersedes: none
title: README
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Research: Knowledge Architecture — Inject vs Query, Multi-Brain, Hooks

User-directed commission (Q1 auto-inject vs on-demand query, Q2 multi-brain
management, Q3 hook role; GCC hint). Primary sources: Glitch Cat Club
(`graph-memory-starter` evals, `prompt-router-starter`, `chief-of-staff-crew`),
Anthropic context engineering, Chroma context-rot, Claude Code hooks.
Headline mechanism fact: **Jcode has no prompt-time context-injection hook**
(observers + `pre_tool` gate only) — the faithful design under Jcode is
hybrid C: minimal static overlay + pre-seeded native memory + on-demand
`ask.py`; multi-brain invariants (one domain/brain, deterministic routing,
build-time intelligence, single-source+regeneration, routed-not-stacked
injection ≤~400 tok, staleness as first-class invariant). Basis for the
`PROGRESS.md` ts-brain.ts cutover open decision.

## Migration note
Cutover 2026-09-05: this record was split out of the shared
`PROCESS/02_research/{findings,open_questions,references}.md` stage files
(research 2 of 2; commission 1 lives in
`RESEARCH/2026-09-02_h720-etth1-research/`). The 2026-09-03 content is
preserved verbatim; the stage folder keeps only its contract.

## Reopen 2026-09-16 — external validation of GCC `graph-memory-starter`
INBOX item `graph-memory-starter.txt` (84.8 KB, 2428 lines, full source of all
53 files) drove a web pass that appends §7 to `findings.md`, closes OQ4 and
OQ7, and adds OQ9–OQ11. Status flipped `done` → `in-progress` for the
duration of the edit, closed back to `done` at the end of the session.
