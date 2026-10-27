---
type: Concept
title: "Progressive Disclosure Depth vs Folder Hierarchy: MCP Gateway and Disclosure Patterns"
source: "https://austegard.com/blog/progressive-disclosure-in-mcp-servers-keeping-llm-context-lean.html"
tags: [context-engineering, icm, progressive-disclosure, planning, anti-leakage]
retrieved: 2026-09-15
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Progressive disclosure is an information-architecture principle that reveals complexity in stages, not a synonym for folder nesting. Retrieved 2026-09-15 from https://austegard.com/blog/progressive-disclosure-in-mcp-servers-keeping-llm-context-lean.html.

ICM folder depth (corpus → graph → digest injection) and disclosure depth (what the agent sees per turn) are orthogonal axes. Folder depth controls corpus organization and build cost; disclosure depth controls per-turn token budget and decision scope. Collapsing them — assuming deeper folders automatically means leaner prompts — hides the real lever.

Naive file-per-endpoint MCP designs waste thousands of tokens on tool schemas before any work starts: ~480 tokens for 8 operations versus ~120 via a gateway pattern (75% reduction). Five to six such servers burn 2,000+ tokens before the conversation begins. This is the ICM analog of injecting full digests or indexes unconditionally.

Gateway tool with action dispatch consolidates operations into one tool with an action discriminator. The LLM sees one schema; full documentation lives behind a discover action invoked only when needed. This separates disclosure depth from storage depth: many corpus pages, one entry-point schema.

On-demand capability discovery keeps the docstring minimal and returns structured guidance (critical rules, action selection, filters) only on discover. Simple requests skip discovery entirely, paying zero documentation tax. Complex workflows pay once per session.

Response-embedded guidance scopes instructions to the data just returned, avoiding stale external prompts. Proactive warnings and default-on response filtering strip fields the LLM will not use (avatars, internal IDs, verbose timestamps) and normalize repeated structures. Compact is default; full fidelity is opt-in.

Design check for ICM: injection budget (e.g., 2000-char digest cap with drill-down via ask.py --tag --raw) plus discover-style tool routing plus compact responses keeps disclosure depth bounded while folder depth grows freely. Evaluation must separate nominal savings (skipping a 150KB index) from measured savings (fewer targeted tool turns), because capable agents self-route and skip indexes regardless.

Provenance: austegard.com (2026-01-06), retrieved 2026-09-15.
