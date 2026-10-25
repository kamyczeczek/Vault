---
type: Concept
title: CONTEXT-MAP
generated: { by: okf-enforcer/0.6, at: 2026-10-23T19:33:45Z }
---

# CONTEXT-MAP.md — workspace

Which bounded contexts exist, where each one lives, and how they relate. This
file describes the *portfolio*; each member describes itself in its own entry
file. Vocabulary is defined once, in `GLOSSARY.md`.

A context is a place where one term means one thing. `Corpus` means one thing in
`datasets` and is not required to mean the same thing in `agentic-research-lab` —
that is the point of a bounded context, and the reason this file maps rather
than unifies.

## Contexts

| Context | Home | Owns | Does not own |
|---|---|---|---|
| Portfolio | this file + `DECISIONS.md` | Project list, grades, cross-project rules | Any project's internals |
| Tool lifecycle | `TOOLS.md` | Grading bars, promotion, demotion | Tool implementation |
| Skills | `skills/` at root, plus a `skills/` home per project | Agent workflow instructions | Project source code |
| Agentic research (archived) | `projects/_archive/agentic-research-lab/` (archived 2026-10-08, `grade: demoted`) | Corpus, knowledge graph, reflection, VERA study (frozen; read-only precedent source for `tools/`) | Retrieval quality (that is `knowledge-retrieval`) |
| Knowledge retrieval | `projects/research/knowledge-retrieval/` | The read path: ranking, quoting, corpus health | Corpus construction (that is ARL) |
| OKF-rag notes | `Notes/OKF-rag/` (not a project — see `handoff/decisions/notes-okf-rag-outside-project-contract.md`) | Artifact vocabulary (hub, slice, `evidence_status`, source vs locator), the evidence contract, the gold set and its benchmark | Ranking, indexes and retrieval systems (that is `retrieval-v2` / `knowledge-retrieval`) |
| Forecasting models | `projects/research/benchmark-core/` | Architectures, the cross-domain benchmark harness | The H720 research line |
| Long-horizon forecasting | `projects/research/etth1-h720/` | H720 ETTh1 accuracy: H2K, SAB-L, AMR-24/168 | General model zoo |
| Model discovery | `projects/research/research-engine/` | Autonomous mutation and discovery loops | Fixed benchmark evaluation |
| Datasets | `projects/_archive/datasets/` (archived 2026-09-27, `grade: demoted`) | Fetchers, catalog, raw inbox | Model training |
| Project brain | `projects/research/brain/` | Derived FTS5 corpus and graph *per project* | The projects' own source |
| Book retrieval | `projects/research/the-pragmatic-programmer-retrieval/` | Single-monograph RAG, RAPTOR, and graph benchmark over "The Pragmatic Programmer" | Cross-project corpus retrieval (that is `knowledge-retrieval` / `retrieval-v2`) |

## Relationships

```
                    skills/ (root, full redundant set)
                    │  vendored on first use into:
                    ▼
   ┌────────────────┬─────────────────┬──────────────────┐
   │  agentic-research-lab            │  brain           │
   │  corpus + graph + reflection     │  derived index   │
   └───────┬────────────────────────┘  └──────────────────┘
           │ produces the corpus
           ▼
   knowledge-retrieval ── measured the read path ──► ARL (archived 2026-10-08)
           (results land in knowledge-retrieval/references/)

   benchmark-core ◄── models evaluated by ──► etth1-h720
        │                                            │
        └──────────── both feed ─────────────────────┘
                     research-engine (mutation/discovery)
                              ▲
                     datasets (archived; was feeding both forecasting projects)
```

Reads, in words:

- `agentic-research-lab` **built** the corpus and the graph (archived 2026-10-08 to `projects/_archive/agentic-research-lab/`; read-only precedent source for `tools/`). `knowledge-retrieval`
  keeps the measurements; results live in `knowledge-retrieval`, never in ARL.
- `brain` is derived state for every project; it is never source.
- `benchmark-core` owns general architectures; `etth1-h720` owns the long-horizon
  line. They are peers, not parent and child — D3 graduation is how code moves
  between them. The dependency is by import, not by containment: each keeps its
  own git history, and neither nests inside the other.
- `datasets` is archived (demoted 2026-09-27); it fed both forecasting projects and owns nothing they build. Rebuild as a new project per D10.

## Grades

Mirrors the `grade:` frontmatter of every project entry file (D4). Sorted so a
reader sees candidates first.

| Grade | Meaning | Projects |
|---|---|---|
| `candidate` | Under evaluation; not yet absorbed by another project | `the-pragmatic-programmer-retrieval` |
| `active` | Real work with a subject of its own | `benchmark-core`, `brain`, `etth1-h720`, `knowledge-retrieval`, `research-engine`, `retrieval-v2` |
| `demoted` | Kept with the measurement that demoted it | `agentic-research-lab` (tools-first split 2026-10-08), `datasets` |

Six projects are `active`, one is `candidate` (`the-pragmatic-programmer-retrieval`); `agentic-research-lab` and `datasets` are `demoted` (archived). A project becomes a `candidate` when a tool is
being evaluated for promotion (D1, `TOOLS.md`); it becomes `demoted` when
something better supersedes it and the measurement is kept.

## Shared substrate

Every project that keeps a knowledge index uses the same shape: a derived
corpus of markdown chunks plus an FTS5 SQLite graph, built from that
project's own sources. `projects/_archive/agentic-research-lab/` holds the reference
implementation (`projects/_archive/agentic-research-lab/scripts/bootstrap_project_brain.py`,
`scripts/ingest.py`, `knowledge/graph/build_graph.py`, paths project-relative).
Other projects either use that tooling or carry their own sidecar under
`.brain/`. The substrate is a convention, not a library — do not couple
projects to each other's internals.

## Shared output shape (always on)

Every user-facing answer, at root and in every project, follows
`skills/i-have-adhd/SKILL.md` (vendored 2026-09-27 from ayghri/i-have-adhd,
MIT): action first, numbered steps, one concrete next step, no
preamble/recap/closers. This overrides the skill's opt-in flag — off only on
"stop adhd mode". No per-project vendoring required for this one: it shapes
the answer, not the work, so the root copy is authoritative (D8 locality
applies to working skills, not to output shape). Not gated: prose shape is
LLM judgment, and a gate that judges prose is the failure
`00_reflection_compaction_variance` documents — declaration plus routing,
not enforcement.

## What is deliberately not shared

- **Forecasting models.** `members/` belongs to `benchmark-core`. Siblings
  import it; none re-vendor it.
- **Graph databases.** Each is derived, gitignored, and rebuildable. Never
  copy one project's `graph.db` into another.
- **Datasets.** Fetched, not vendored. `datasets/` (archived) owned the
  fetchers; every other project re-fetches rather than checking in a copy.

One home per fact; link, never copy. A second copy of a fact is a second
home, and it drifts (recorded in `PHILOSOPHY.md` §2). This file is the one
home of the portfolio map — nothing at the root restates it.

## Shared vocabulary

Terms with more than one plausible home live in `GLOSSARY.md` once. Each
project's `CONTEXT.md` may add a `## Language` section for terms **local to that
project**; a term in the glossary is never redefined locally, only narrowed.
If a project needs a different meaning for a glossary term, that is a conflict
to record in `DECISIONS.md`, not a second definition to add.

## Routing new research requests

**Research request** (see `GLOSSARY.md`): an open problem set up for
investigation, with no owning project yet. This section is the decision
procedure — shape first, domain as tiebreaker — not another copy of the
project list above.

Decision order:

1. Match the *shape of the question* against `AGENTS.md` "Where to go".
   One line wins.
2. If two lines fit, resolve with each project's *Does not own* column and
   the relationship notes above, then **declare the destination in one line**
   before starting work ("routing to `knowledge-retrieval`: you ask about
   ranking, not about building the corpus"). The owner redirects with one word.
3. If no line fits, it is a new subject: scaffold a candidate project
   (`grade: candidate`, skeleton below) and add its row to the routing table
   in `AGENTS.md`.

Structure: all live projects are folded into one group folder,
`projects/research/` (2026-10-03). Deliberately no themed subfolders inside it,
and `projects/_archive/` stays at the portfolio root, ungated (D10). The routing
decision lives in this file, not on the shelf.

Human check: read `CLAUDE.md` as if you had no memory of the workspace — can
you name, for any task you care about, the one project to open? If not, fix
the routing table (here or in `AGENTS.md` §"Where to go"), not the projects.

### Candidate project skeleton

Two files minimum, everything else lazily:

- `CLAUDE.md` — identity, `grade: candidate` frontmatter, the open question,
  plus one new line in the table above
- `CONTEXT.md` — the research question, the first concrete step, `## Open work`

Demotion is painless (two-stage archive, D10) because nothing else exists yet.
When the first candidate appears, persist a scaffold script (`scripts/new_project.py`) —
not before.

## The root gate

`scripts/check_workspace_integrity.py` — the only check that sees the workspace
root; it also runs as gate Q0 on every live-project commit, before
the other seventeen. It exists because of a specific, observed failure: every
project gate resolves its root to its own repository, so the one directory
they cannot see is the one above them — during the restructure that produced
this portfolio, a malformed shell command left two files literally named
`$(git` and `'` at the root, and every project gate passed with both files
sitting there.

Which check is which, which are hard and which advisory, and how a
root-level entry gets added: the gate's own docstring is the single home.
Nothing in this file or any other restates it.

The rule the gate encodes, in one line: **use a function call where a
function call will do.** Both incident files were created by a compound
shell command whose quoting broke — one unterminated quote, one split
command substitution. Neither is a class of error a person reliably avoids
by trying harder; both vanish if there is no shell in the path.
