# PHILOSOPHY.md — workspace

Why this workspace is shaped the way it is. Principles first, then what the
workspace already proved. Details live in `DECISIONS.md` and each project's
`EXPERIENCE.md` — this file links, never copies.

## 1. A good working complex system emerges from many small, good working, easy-to-test systems

Gall's law: a complex system that works invariably evolved from a simple
system that worked. A complex system designed from scratch never works.

The loop: build the smallest useful thing → verify it → compose with another
verified piece → verify the composition → repeat. Architecture emerges from
what actually works, not from what was planned. Interfaces are discovered
from both sides already built, not invented upfront.

This is also how agents work best: one small piece with clear inputs,
outputs, and a test — never "build the whole system". And how humans learn
systems: one working piece at a time.

Top-down has its place — vision, fixed external interfaces, compliance,
large-team coordination. Rule of thumb: **top-down for vision, bottom-up
for execution.**

## 2. What this workspace already proved

- **Small means few roles, not few files** (`DECISIONS.md` D5). A 10k-file
  corpus is one role; a 20-file project with five jobs is five projects.
- **One folder, one job** (`CLAUDE.md` Rules). A project serving two subjects
  is two projects.
- **Link, never copy** (`CONTEXT-MAP.md` §What is deliberately not shared). One home per fact; a second
  home drifts. Graduation is copy-then-delete in one commit (D3).
- **Contracts before composition** (`CONTEXT.md` per project: inputs,
  process, outputs, one human check). The merge is trivial; the boundaries
  are not (D12).
- **Verify the composition, not just the pieces.** 15 local-property gates
  passed continuously through six relational defects
  (`knowledge-retrieval/EXPERIENCE.md` §4, `agentic-research-lab/
  EXPERIENCE.md` §2). A gate asserts what the composition guarantees.
- **A gate must be able to fail** — mutation-test it before trusting it
  (`agentic-research-lab/EXPERIENCE.md` §3).
- **Measure the system, not the annotation.** A metric no improvement can
  move is the wrong metric — retire it, write down why
  (`knowledge-retrieval/EXPERIENCE.md` §1).
- **A single run is a hint, not a result** (`benchmark-core/EXPERIENCE.md`
  §4). Mean ± std, rolling origins, significance or it didn't happen.
- **Kill budget: two iterations, then kill** (`etth1-h720/EXPERIENCE.md` §3).
  A third tuning round on a rejected candidate is how a loss becomes a habit.
- **Quarantine the piece, never the whole** (`datasets/EXPERIENCE.md` §8,
  `knowledge-retrieval/EXPERIENCE.md` §2). Damage is local; the record stays.
- **Experience is local; distillation is on demand** (D11). Each project
  gathers its own in `EXPERIENCE.md` + `docs/adr/`; the root links. A lesson
  graduates here only after appearing independently in ≥2 projects.
- **Archive in two stages** (D10): `grade: demoted` with the measurement in
  place → `projects/_archive/` (ungated graveyard) after cooling.
- **Fail fast, cheap, and typed** (`agentic-research-lab/EXPERIENCE.md`
  §11). Two failures or one ambiguity → abort, re-plan, hand off state.

## 3. How to use this file

New to the workspace: read §1, then `AGENTS.md` for where to go.
Adding a principle: only from a lesson already written in a project's
`EXPERIENCE.md` with evidence attached — never from aspiration.
Disagreeing: open a `docs/adr/` entry in the project it affects; if the same
lesson lands in a second project, graduate it here.
