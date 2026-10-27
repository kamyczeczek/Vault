---
type: Concept
id: 00_pocock_context_shared_language
title: "pocock-context-shared-language.md"
source: "pocock-context-shared-language.md"
tags: [icm, context-engineering, context-md, glossary, domain-modeling, planning, agentic, agents]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

CONTEXT.md is the ubiquitous language (Evans DDD) that makes agents concise. Example from Pocock: BEFORE "problem when a lesson inside a section of a course is made real (i.e. given a spot in file system)" → AFTER "problem with the materialization cascade" — one term replaces 20 words, tokens + naming + navigation improve every session.

Domain-modeling is the active discipline for changing the model (not just reading CONTEXT.md). File structure: single context = `/CONTEXT.md` + `/docs/adr/*.md`; multi-context = `/CONTEXT-MAP.md` pointing to `/src/<context>/CONTEXT.md`. Create lazily — only when first term/ADR needed.

During session: challenge terms against glossary immediately ("glossary says cancellation = X, you mean Y?"); sharpen fuzzy language into canonical terms (account → Customer vs User); stress-test with concrete edge-case scenarios; cross-reference with code and surface contradictions; update CONTEXT.md inline as terms resolve (no batching), strictly glossary — no implementation details, no spec/scratch pad.

Offer ADR only when all three hold: (1) hard to reverse, (2) surprising without context, (3) real trade-off among alternatives. Otherwise skip. Format via CONTEXT-FORMAT.md / ADR-FORMAT.md.

Implication for workspace-research: CONTEXT.md is the L3→L2 bridge. Keep it as glossary (terms like fingerprint, digest, route, leaf, reflect) so ask.py --tag routing and digest injection don't drift; ADRs record hard choices (graph fingerprint gate, closed prompts). Grilling builds it; writing-for-agents keeps its pointers tight.

Provenance: mattpocock/skills domain-modeling/SKILL.md + CONTEXT-FORMAT.md retrieved 2026-09-15.
