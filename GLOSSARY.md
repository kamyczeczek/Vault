# GLOSSARY.md — workspace

The vocabulary of this workspace. One home per term; if a project defines a term
differently, that is a conflict to resolve, not a second definition to add.

**Project**:
A folder under `projects/research/` that owns exactly one subject and answers for its own
inputs, outputs, and gates. The unit of work. Not the unit of knowledge, and not
a stage in a pipeline.
_Avoid_: workspace, repo (for the root), subworkspace, module

**Root**:
This directory. It holds the catalog, the contracts, and the folders that are not
projects. It is not a project; it is version-controlled (D6).
_Avoid_: workspace root (fine, but do not call the root itself a workspace)

**Portfolio**:
The set of projects plus the relationships between them. Described in
`CONTEXT-MAP.md`; the individual members are described by their own entry files.
_Avoid_: workspace (see Root), collection, monorepo

**Tool**:
A capability being built, tested, or polished for effectiveness. Until it is
graded, a tool is a project like any other — see `DECISIONS.md` D1.
_Avoid_: utility, script (too small a word), library (implies shared, see Skill)

**Grade**:
The verdict on a tool: **PROMOTE** (works, meet the bar, merge into a project),
**REJECT** (does not work, keep the negative result), **DEMOTED** (worked, no
longer earns its place, keep with the measurement that demoted it). Same
vocabulary the forecasting models use.
_Avoid_: status (untyped), stage (conflicts with pipeline stages)

**Open work**:
Work a project knows it has not finished, recorded where a reader will hit it —
in the project that owns it. Not a root-level list.
_Avoid_: backlog, TODO (TODO is a code annotation, not a record), issues

**Carry**:
A project retains its negative results — what was tried, what failed, what is
still open — alongside what works. Carrying is a property of the project, not a
separate document to remember to write.
_Avoid_: archive (that is a *home*, not a state), history

**Contract**:
A project's `CONTEXT.md`: inputs, process, outputs, one human check. The
`icm-architect` sense, not the glossary sense.
_Avoid_: spec, README, documentation

**Glossary**:
This file and the `## Language` sections inside project contracts. Vocabulary
only, no implementation.
_Avoid_: dictionary, terminology

**Research request**:
An open problem set up for investigation, with no owning project yet. The
routing decision — which project owns it, or a new candidate project — is made
by the procedure in `CONTEXT-MAP.md` §"Routing new research requests".
_Avoid_: "research" for continuing work inside a project (that is its open
work), a new model (that is `research-engine`), a pipeline run (project-local)

**Context map**:
`CONTEXT-MAP.md` — which contexts exist, where each lives, how they relate.
_Avoid_: index, catalog (that is `CLAUDE.md`)

**Skill**:
A shared, reusable workflow package under `skills/`. One home, referenced by
every project. Not a tool: a skill is instructions, a tool is code.
_Avoid_: plugin, library, template

**Experience**:
Distilled good practices a project learned from its own work. Lives in that
project (`docs/adr/` per decision, optional `EXPERIENCE.md` on demand — D11).
The root links to it; it never copies it.
_Avoid_: best practices (unowned), learnings (vague), wiki

**Archive**:
The home `projects/_archive/` for finished work. Ungated, unrouted (D10).
Stage 1 is `grade: demoted` in place; stage 2 is the move here.
_Avoid_: ARCHIVE (uppercase duplicate), backup, old

**Forge**:
`forge-guardrails` (antoinezambelli/forge), integrated into `agentic-research-lab`
as an opt-in reliability layer for **weaker/cheaper remote models** doing
multi-step tool-calling (OpenAI-compatible endpoints, e.g. nara/omniroute):
rescue parsing, retry nudging, response validation, context compaction.
Self-hosted serving is *not* the use case. Installed in the project-local
`.venv-forge` (Python 3.12); wired via `scripts/forge_bridge.py`.
ADR 0017. The PyPI `forge` package is a *different* project (Django scaffolding)
— never install by name.
_Avoid_: forge (lowercase, the PyPI Django package), AgentForge (DataBassGit), SDK

**Pack**:
A `.txt` bundle built by `scripts/build_notebook_pack.py`: Shelf A workspace
context at a chosen depth (`--level 0/1/2`, `--scope root/project`) + Shelf B
recent sessions + Shelf C grill + Shelf D expert slot. Derived, gitignored,
reproducible. Not a run: the pack carries no question.
_Avoid_: dump, export (too vague), source (that is the NotebookLM side)

**Run** (notebook run):
One tracked pipeline execution: `handoff/notebook-runs/<YYYY-MM-DD-slug>/`
with `problem.md` (the defined problem, uploaded as a citable source) +
`answer.md` (the raw NotebookLM answer with citations). Primary, tracked —
NotebookLM is nondeterministic, so a run cannot be rebuilt from the pack.
_Avoid_: session (that is an agent transcript), query (that is one question)

**Problem**:
The single defined question a run asks, stored as `problem.md`
(context / decisions to take / constraints). Narrow enough that the answer is
promotable to exactly one flag, ADR, or scar.
_Avoid_: topic, thread, research request (that is pre-routing)
