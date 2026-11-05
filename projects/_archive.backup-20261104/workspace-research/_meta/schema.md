---
type: Concept
title: schema
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# Schema — workspace-research

The closed set of note types, chunk naming conventions, and metadata labels for this workspace.

## 1. File Roles & Locations

| Role | Path | Description |
|---|---|---|
| **Catalog (L0)** | `CLAUDE.md`, `AGENTS.md` | Single-screen identity and routing map |
| **Contract (L1/L2)** | `CONTEXT.md`, `stages/*/CONTEXT.md` | Workspace operating model and stage execution contracts |
| **Pipeline (P1)** | `pipeline/WORKFLOW.md` | Global ordered phase specification (01→02→03→04→05) |
| **Factory / Source (L3)** | `knowledge/corpus/*.md` | Canonical markdown knowledge chunks (source of truth) |
| **Derived Brain (L3)** | `knowledge/graph/` | SQLite FTS5 database, graph index, and `GRAPH-DIGEST.md` |
| **Vocabulary** | `knowledge/topics.md` | Controlled list of valid topic tags for routing |
| **Skills Catalog (L1)** | `skills/` | 46 reusable task execution packages (`skills/SKILLS.md`) |
| **Product (L4)** | `reflection/digests/`, `reflection/candidates/` | Provenance-stamped reflection digests and state-machine candidates |
| **Persistent Memory** | `reflection/memory.md` | Promoted accepted rules; contracted read-path for reflection |

## 2. Chunk Frontmatter Schema (`knowledge/corpus/NN_slug.md`)

Every corpus chunk must adhere to:
```yaml
---
id: NN_slug               # Must match the filename stem exactly
title: "Human Title"       # Descriptive title (e.g. including (part X/Y) if split)
source: "raw_filename"     # Exact matching filename in knowledge/raw/
tags: [tag1, tag2]         # Tags from knowledge/topics.md
---
```

## 3. Reflection Candidate Schema (`reflection/candidates/<topic>.jsonl`)

Each line is a single JSON object:
```json
{
  "id": "candidate-slug",
  "state": "proposed",
  "claim": "Clear declarative assertion",
  "evidence": ["chunk_id_1", "chunk_id_2"],
  "bet": "Next experimental verification step",
  "provenance": {
    "fingerprint": "12-hex-corpus-hash",
    "plan_version": "12-hex-workflow-sha",
    "phase": "04_reflect"
  }
}
```
Valid states: `proposed` -> `experimental` -> `accepted` | `rejected`.
