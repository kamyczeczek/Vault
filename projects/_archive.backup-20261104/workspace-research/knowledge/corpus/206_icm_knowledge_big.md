---
type: Concept
id: 206_icm_knowledge_big
title: "ICM_knowledge.md (part 207/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

— an extensible list (Project, Memory, Reflective, Gratitude, Reference)

Every skill file resolves paths at runtime by reading this config. Nothing is hardcoded.

journal.config.md

— one per journal, produced by the Phase 0 setup interview. It is the authoritative filter. It contains:

Journal metadata (name, slug, type, creation date, framing primer)

list (label, description, priority, shape) — the only labels the AI may cite in a Filter Line

— the threshold for surfacing vs. letting pass (a prose rule)

Does NOT belong

— explicit exclusions

Voices that trigger capture

— whose words count

ingest_sensitivity

(generous / conservative)

seeds_enabled

(boolean, per journal)

— optional motto shown on the diary’s title page

These two config files make the system fully declarative. The agent applies rules, never invents them.

------

1. Agent workflows (the     “skill” files)

The system is a set of plain-text instruction files (

grail-listener.md

grail-capture.md

grail-criteria-review.md

) plus a governing

. They are meant to be loaded into an AI agent (Claude Code or any agent that can read a folder and edit files). They define three phases:

Phase 0 — Listener (

grail-listener.md

A structured 9‑question interview that excavates a journal’s criteria from the owner in their own words. It:

Asks one question at a time, forbids the AI from proposing criteria or interpreting answers

Records answers verbatim or with explicit owner-confirmed light edits

journal.config.md

, scaffolds the journal folder (

_candidates.md

_session.md

, optionally

Runs a self-check that every criterion traces to the owner’s words before writing

Phase 1 — Capture (

grail-capture.md

The capture discipline. It defines the

Filter Line

as the only allowed surfacing message: a verbatim quote and the matched criterion label. It implements four entry points:

(owner says “Grail this”) → writes straight to

(session watch mode) → surfaces candidates one at a time as material clears a criterion + the bar

(process a transcript) → reads the full source, collects all matches, ranks them, writes up to the cap into

_candidates.md

; the owner later drains the file with

keep/refine/drop/context

one candidate at a time

(walk old notes) → walks the owner’s existing archives or sticky notes one note at a time against a target journal’s criteria, with

The phase also enforces Grail Rule 2 (no to-dos in the diary), defines the render‑ready entry shape (thin frontmatter, single unstructured body), handles duplicate detection and theme entries, and manages session state via

_session.md

Phase 1.5 — Criteria Review (

grail-criteria-review.md
