---
type: Concept
id: 247_icm_knowledge_big
title: "ICM_knowledge.md (part 248/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Next turn: [Call dispatch.py questions.] [Task 2's worker surfaced NEEDS_GUIDANCE: "JWT vs random hex token patterns both exist in this codebase, need a design call."] [You show Ari the question block near the top of your response. Ari replies: "random hex, simpler and safer."] [You call dispatch.py answer w-a3f2-impl-reset --answer "random hex, simpler and safer" — a fresh worker spawns with the answer baked in.] [Meanwhile task 1 and 4 have completed; you check their logs, review, move on.] [Trivial one-liner at the end (rename a constant) → inline Agent tool on haiku.] [Review all changes yourself.]

The whole flow happens without Ari ever opening a new Claude window, pasting

anything, or watching a long-running task. Main session stays on Opus and in

the orchestrator seat. Execution is invisible.

Integration with Other Skills

superpowers:writing-plans

first if the task needs a detailed plan

superpowers:using-git-worktrees

for isolation

Executors should follow

superpowers:test-driven-development

when writing code

After all tasks, use

superpowers:verification-before-completion

before claiming done

------

david vogel\David and Jake's Picks V2\I run four phases before any AI builds anything\crush-architecture.md

------

workspace: crush

role: reference

CRUSH_ Architecture Reference

Full technical architecture, effect details, struct layouts, gotchas. Referenced from [[CRUSH_/CLAUDE|CRUSH_ CLAUDE.md]] — load on demand during development.

------

Architecture

The .crush Build-Time Generator

Effects are authored as

JSON files (UI param definitions + shader references) in

. The Python

script generates all C++ OFX boilerplate at compile time — parameter definitions, uniform bindings, visibility logic, effect registry, and param fetch dispatch for all 6 effect slots.

C++17, Objective-C++, Metal Shading Language (MSL), Python (generator)

#### Graphics API:

Apple Metal (zero-copy GPU pipeline)

#### Host Target:

DaVinci Resolve (OpenFX). After Effects port deferred.

6-Slot Effect Chain

The plugin supports up to 6 chained effects in a single instance with progressive reveal:

dropdown — primary effect (slot 1, always visible, no "None")

dropdowns — chain slots (default "None", hidden until previous slot is populated)

When user sets Effect 2, Effect 3 dropdown appears. Set Effect 3, Effect 4 appears. Up to 6.

Rendering: N-pass chain. Each pass reads from the previous pass's output (dst buffer).

DECIMATE applies ONLY on the final pass, after all chained effects.

Global Controls (always visible, not per-effect)

(0-1) — directional pixel melt. Per-column/row drip offset from multi-octave noise, chromatic aberration, black data loss for off-frame pixels. Full color preservation — source pixel taken exactly, no decay.

DECIMATE Direction

— Down, Up, Left, Right
