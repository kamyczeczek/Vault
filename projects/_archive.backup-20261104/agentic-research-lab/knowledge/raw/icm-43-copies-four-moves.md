---
type: Concept
title: "ICM Four Moves: Interview → Map → Proposal → Copy-Then-Verify (43-Copy Cleanup)"
source: "https://arxiv.org/html/2603.16021v2 + transcript: How I Fixed a 43-Copy Claude Code Mess (Jake Van Clief / Mason case)"
tags: [context-engineering, icm, workspace-research, planning, anti-leakage, reflection]
retrieved: 2026-09-15
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

Problem the video names as drift/leak/repeat: a practitioner (Mason, 5am DM) had a notes vault "Grock Brain" with 4 AIs each on its own status page and no shared source of truth, plus 12 Claude Code side copies + 5 project folders, totalling 43 side copies (GitHub worktree-style clones) that never merged back to the brain. Three symptoms: drift (no desk/map → guesses drift), leak (decisions trapped in chats, chat gone = decision gone), repeat (no identity file → user is the file every time).

ICM solves it with one folder as the agent. Van Clief paper (2603.16021v2, Mar 2026) formalizes: filesystem replaces framework. Five-layer hierarchy: L0 identity (who you are / CLAUDE.md), L1 routing (where jobs live), L2 stage contract (CONTEXT.md Inputs/Process/Outputs), L3 factory (reference, stable), L4 working artifacts (per-run output). Numbered folders encode order; output/ is the handoff. One agent reads different context per stage; subagents inherit scope from the same tree. Local scripts handle mechanics.

Four moves (each writes one file, no code moved before approval):

1. Interview — AI asks one question at a time ("What do you run? Where does each thing live? Which AI knows what?"); only the human's words go on record. No guessing. Runtime: extended Q&A; Mason DM'd "How many questions lol?"
2. Map — inventory of every business, file location, AI, and every side copy. Unknown stays unknown. The map counted the 43 copies Mason didn't know he had. Three places held the only copy of something; four AIs (Claude/Grok/Hermes/OpenClaw); 18 code folders inside ~/brain.
3. Proposal — smallest folder that holds the map; creates nothing, moves nothing. Human reads the map and catches what AI can't: folder landed in Downloads not brain, interview ran in a side copy, start file 130 lines with deferred pushes. Gate before any mutation.
4. Final move — copy-then-verify: AI copies files into the new folder (originals stay), opens three copies to confirm reads, then deletes originals only after verification. Decisions file gets one line per chat-trapped decision, chat then done. Cold walk test: fresh AI opens only the start file and must route to one real job unaided; if it fails, fix the start file and retest. Mason's result: 16 new files, 2 folders, nothing deleted, no code folder touched; start file 130→46 lines (routes only); 43 copies listed not merged; only 3 decisions still trapped because a 24-morning log had already carried the rest.

Implication for this brain: keep the same gates — INBOX→corpus→graph (build_graph fingerprint), reflection only via leaves/rollup, and a cold-walk equivalent (fresh agent must route via ask.py --tag). Treat side copies/worktrees as drift signal, not source to auto-merge.

Provenance: Van Clief 2603.16021v2 via Exa + Jina (retrieved 2026-09-15) + verbatim transcript of the 43-copy video (Mason case, four moves, cold walk test).
