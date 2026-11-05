---
type: Concept
id: 2026-09-05_antifragile-workspace-design
date: 2026-09-05
scenario: S4
surface: antifragile agent-workspace design — accumulating strength from problems, reducing slop over time
status: done
supersedes: none
title: README
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Research: Antifragile Workspace Design

Question: what makes an agent workspace become stronger and more
efficient with time — producing less and less slop, so that every
problem it survives leaves it stronger (the user's thesis)? Method
(user-directed): a **graph-fed claims ledger** — the 14 INBOX sources
are reduced to provenance-tagged claims; the workspace's own brains
(`icm_brain`, `reflection_brain`) are queried per claim cluster for
prior positions; contradictions are logged explicitly; synthesis
reads the ledger + graph queries, never re-loading bulk sources.
Headline findings live in `findings.md`; unresolved tensions in
`open_questions.md`.

**Close state:** 33 claims in 8 clusters (A–H) with per-cluster graph
checks; 5 conflicts/tensions resolved or bounded; 4 S-candidate gaps
(R1–R4) routed. Sources preserved in `sources/` (byte-verified before
INBOX purge). G1–G3 (ICM expansions, slice-verified absent) ingested
as icm_brain corpus chunks (`antifragile_research_*.md`, 3 files) —
graph rebuilt, live-query proven. Distilled findings + the method
itself seeded as project memory cards.

## Route
`RESEARCH/CONTEXT.md` §"Deterministic routing", row R-03.

## Status
- done — exit contract of `RESEARCH/CONTEXT.md` satisfied
  (4 canonical artifacts; check_catalog green; INBOX purged Rule 5).
