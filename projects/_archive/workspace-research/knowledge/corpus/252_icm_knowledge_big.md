---
type: Concept
id: 252_icm_knowledge_big
title: "ICM_knowledge.md (part 253/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

The 1,000-line limit applies to code only. Documentation comments, file headers, and inline documentation do NOT count toward this limit. This limit exists to enforce efficient, concise code — not to punish well-documented code.

Prefer more files with fewer functions each

Every function in a file must logically belong there — don't put camera rotation functions in a text editor file

Split where it makes semantic sense, not just to hit a number

The folder nesting structure exists to support these smaller units

Library-First Design

Write all code as if every function could be extracted into a standalone library. The end goal is maximum reusability across projects.

#### Principles:

Functions should be self-contained with minimal external dependencies

Clean, well-defined interfaces — inputs and outputs should be obvious

Avoid hard-coded project-specific values inside reusable logic — pass them as parameters

Group related functions that could form a library into their own files/modules

In any language that supports libraries (C, Rust, JS/TS, Swift, etc.), structure code so extraction into a library requires moving files, not rewriting them

For C specifically: This is the primary target. Every utility, algorithm, data structure, and system abstraction should be written as a reusable library from day one. Headers define the public API contract, source files contain the implementation. A well-written C library can be linked into any project.

No Auto-Save / No Background Persistence

Every write to a database, file, or storage must trace back to a deliberate user action. No exceptions unless explicitly requested.

#### Never implement:

Auto-saving as the user types

Debounced save on input change

Watchers that persist reactive state changes

Background sync intervals

Persisting UI state automatically (sidebar position, tab selection, scroll)

Writing to storage on mount/unmount/navigation

#### Always require:

User clicks "Save" → write

User submits form → persist

User explicitly toggles setting → save

User confirms action → execute

Pattern: User Action → Service Call → Write → Confirm Success

Folder Nesting as Navigation

Directories are not just organization — they're how you navigate. The tree structure should let you drill down to the right file by following a logical path, not by guessing or searching.

#### Principles:

Group by domain/feature, not by file type (prefer auth/authService.ts over services/auth.ts when the module is complex enough)

Each directory should have a clear, single purpose

Nesting depth should match conceptual depth — don't nest just for nesting, don't flatten when there's real hierarchy

A directory with 1 file is usually wrong — either the file belongs in the parent or more files belong in the directory

Error Transparency

Never swallow errors silently

Catch at service boundaries where you can show user feedback

Log technical details (console.error with context)
