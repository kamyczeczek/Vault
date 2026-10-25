---
type: Concept
status: decided
recommendation: Notes/OKF-rag stays outside the project contract; machinery in root scripts/, gate in root integrity, vocabulary in its own CONTEXT.md
decided_at: 2026-10-25
owner: mateusz
title: notes-okf-rag-outside-project-contract
generated: { by: opencode, at: 2026-10-25T00:00:00Z }
---

# notes-okf-rag-outside-project-contract

`Notes/OKF-rag/` holds a working retrieval loop — gold set, runner, source
slices, evidence contract — but it is not a project: no `preflight.py`, no
`GATES.md`, nothing that can fail. The decision is to keep it that way and put
the machinery where a gate can run: code in root `scripts/`, checks in
`scripts/check_workspace_integrity.py`, notes and vocabulary in
`Notes/OKF-rag/`. Creating a project for three artifacts would buy a contract
for a folder that already has one owner.

Not a fifth retrieval home. `Notes/OKF-rag` is a navigation and evidence
layer over the notes corpus; if it ever grows into a retrieval *system*, it
needs a grade and a decision: absorb it into `retrieval-v2` or demote it.

Recorded here rather than in `docs/adr/`, which does not exist at root; this
directory is the workspace's decision home and `scripts/build_status.py` reads
its `status: open` entries.

## Options rejected

- **New project `projects/research/vault-retrieval/`** — a full ICM shell
  (preflight, CONTEXT, GATES, MAP, grade) around one JSON file, one skill and
  one check. The structure would cost more than the work it guards.
- **Fold into `projects/research/knowledge-retrieval/`** — that context owns a
  different system (chunk store, graph, hybrid). Two unrelated systems under
  one owner is how the earlier `agentic-research-lab` gates ended up pointing
  at archived code.

## Consequences

- The gate starts as **advisory** and becomes hard only after the note
  migration lands; a gate that is red on its first commit teaches agents to
  route around gates.
- `Notes/OKF-rag/CONTEXT.md` owns the vocabulary (`hub`, `slice`,
  `evidence_status`, `source` vs `locator`). The *procedure* stays in
  `skills/retrieval-two-stage/` and `DECISION-kontrakt-odpowiedzi-retrieval.md`
  — three homes, one per kind of claim, no restatement.
- Slices stay a navigation aid: `_slices/` is derived, `origin_hash` is
  checked, and an excerpt never rises to `direct` evidence without reading the
  origin file.
