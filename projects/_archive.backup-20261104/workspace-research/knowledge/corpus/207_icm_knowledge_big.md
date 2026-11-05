---
type: Concept
id: 207_icm_knowledge_big
title: "ICM_knowledge.md (part 208/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

A tuning pass the owner invokes after ingest batches. It reads signal only from the surfacing layer (candidate volume, overflow flags, drop patterns from the current session) and lets the owner sharpen, add, or tighten criteria — always in their own words. It never reads the diary entries themselves (that would be the agent connecting).

These skill files are the “software.” The agent carries them out by reading/writing Markdown files, exactly as instructed.

------

1. Rendering layer

build-diary.js

— a plain Node.js script with zero dependencies. Run as:

node build-diary.js my-book

Scaffolds the HTML diary from

diary-template/index.html

on first run.

Reads all confirmed entries from

journals//entries/\*.md

, parses their frontmatter and body.

Reads the journal’s config (

journal.config.md

) and the owner name from

grail.config.md

#### Injects three data blocks into the HTML template as JavaScript constants:

(array of entry objects),

(title page metadata), and

(the verbatim capture criteria, bar, and priority lens).

The resulting HTML file lives at

journals//diary/index.html

and opens directly in a browser with no server.

diary-template/index.html

— a self-contained, vanilla JavaScript/CSS “flippable book” with:

A closed leather cover that swings open on click (CSS 3D transforms)

Left/right page leaves with aged-paper textures, foxing, edge darkening, and a center crease

A fixed front‑matter opening: title page (left) and the rules for capture verbatim (right)

Entry scraps laid out with a max of 2 per leaf; length‑based sizing (short quotes render larger, italic, with a gilt rule)

Shuffle‑on‑open: every load or reshuffle re‑deals unpinned scraps using Fisher‑Yates

Pinning: clicking a wax‑seal icon pins a scrap to its current spot; pins persist in

localStorage

keyed by journal slug. Pinned scraps hold their position while the rest shuffle.

Optional theme sketches: hand‑drawn margin art mapped to criterion labels, placed only in the bottom‑right corner of right‑hand leaves.

Full keyboard navigation, swipe gestures, reduced‑motion support, and responsive single‑leaf fallback for narrow screens.

The renderer is a pure presentation layer — it never mutates source

files. The source of truth remains the Markdown entries.

------

1. The guardrails in the     architecture

#### Every design choice enforces the “system surfaces, human connects” boundary:

No auto‑promotion

— ingest candidates never become entries without explicit human keep/refine

No rejection logs

— dropped candidates disappear; the AI’s guesses don’t accumulate into a shadow opinion

Cap overflow flagging

— if an ingest finds more than the cap, the real count is reported; silence would be a hidden filter

No auto‑invoked criteria review

— the owner must call for tuning

Seed mechanics

— raw material that cleared the bar but isn’t ready sits untouched, revisited later by the owner
