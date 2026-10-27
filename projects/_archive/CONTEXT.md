---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# CONTEXT.md — _archive

One job: hold the record of what a project was before the ICM restructure, so the
reasoning behind the current structure survives.

## Inputs

- Reference (every run): the `CLAUDE.md` of the project that superseded this one
- Reference (every run): the split target's own history

## Process

1. Nothing here is ever executed. This folder is read, not run.
2. When a file is superseded, it moves here with the reason, not a copy of the
   current state.
3. An archived repository keeps its own `.git`. That history is the only record of
   the pre-split structure.

## Outputs

- None. This folder produces nothing.

## Human check

Ask: does anything live route here? If a live project imports a file from this
folder, the split was wrong — fix the split, not the import. The archive must be
inert, because the moment it is a dependency it stops being a record and becomes
a second, competing source of truth.

## Why archive instead of delete

`agentic-research-lab/CONTEXT.md` is a running log of defects found and fixed. Its
value is the sequence: which defect was found first, which gate was written
afterwards, which fix was reverted and why. A repository whose history contains
only the fixed version cannot answer any of those questions. The same applies here
— the one-off `fix_*` scripts record what was broken in `bench.py`, and a future
reader hitting the same bug will find that record only if it was kept.
