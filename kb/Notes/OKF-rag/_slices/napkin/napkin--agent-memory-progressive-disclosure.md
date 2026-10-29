---
type: source-slice
title: "napkin — agent memory system: progressive disclosure levels 0–3"
generated: true
origin: "Notes/OKF-rag/napkin.md"
origin_hash: efb8aa584a857a3b28207838b0b63386d045aa4cc87e3856a279d2e0e4545aa8
source_lines: [3094, 3147]
source_heading: "Agent Memory System — Progressive Disclosure"
slice_hash: cd0d4768bcc1a686765a4e5c5dc36a4e0a97e997e3525d8081bb14f6a4ee0e55
generator: "scripts/generate_source_slices.py@1"
---

<!-- GENERATED FILE: do not edit by hand. -->

# napkin — agent memory system: progressive disclosure levels 0–3

## Source excerpt

# Agent Memory System — Progressive Disclosure

> napkin as a structured memory system for AI agents, built on progressive disclosure.

## Core Idea

Agents work best when information is revealed gradually rather than dumped all at once. Instead of vector search, we use a four-level disclosure model (Levels 0–3) that respects context windows and gives agents control over how deep they go.

## Levels of Disclosure

### Level 0 — Pinned Context
A small "always loaded" note the agent reads on every session. Like CLAUDE.md but for the knowledge base. Contains project goals, conventions, key decisions. Should fit in ~500 tokens.

### Level 1 — Overview Map
A generated index of the entire vault. Directory tree with search-validated domain keywords per folder — the words an agent can actually search to land in that folder. Gives the agent orientation — a table of contents for the vault. Target: ~1-2K tokens max. Tags are available in `--json` but excluded from the primer: they cost tokens without carrying routing signal.

Example output:
```
projects/
  keywords: roadmap, Q2, launch, pricing
  notes: 4
projects/napkin/
  keywords: CLI, obsidian, markdown, agent, memory
  notes: 7
people/
  keywords: hiring, team, 1on1
  notes: 12
```

### Level 2 — Search with Snippets
Agent searches using keywords from the overview. Results return partial content — matched keywords highlighted with a context window (~3 lines) around each match. Never full files.

Ranking signals:
- **BM25** — term frequency / inverse document frequency
- **PageRank via backlinks** — notes with more inbound links rank higher (Obsidian link graph is a natural fit)
- **Recency** — file mtime as a tiebreaker

Example output:
```
projects/napkin/architecture.md (score: 8.2, links: 5, modified: 2d ago)
  L14: ...the CLI operates on **markdown files** directly, no Obsidian app...
  L42: ...progressive disclosure model with three **levels** of detail...

daily/2026-03-13.md (score: 6.1, links: 1, modified: 2d ago)
  L8: ...discussed **memory** system design with the team...
```

### Level 3 — Read
Open and read full files. Already implemented via `napkin read`.

## Templates

Different domains need different vault structures AND different Level 1 overviews.

## Provenance

- Origin: `Notes/OKF-rag/napkin.md:3094-3147`
- Origin hash: `efb8aa584a857a3b28207838b0b63386d045aa4cc87e3856a279d2e0e4545aa8`
- Regenerate with `python scripts/generate_source_slices.py`.
