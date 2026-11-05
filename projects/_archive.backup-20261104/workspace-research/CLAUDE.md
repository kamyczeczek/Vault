---
type: Concept
title: CLAUDE
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# CLAUDE.md — workspace-research

Knowledge base for context engineering, ICM rules, and agent/workspace design.
Replicates the proven `ts-research` architecture: corpus markdown -> derived graph -> reflection.

## Where things live

| Path | Role | Description |
|---|---|---|
| `CLAUDE.md` | Catalog (L0) | Entry point and workspace map (this file) |
| `CONTEXT.md` | Contract (L1) | Root operating contract and chunk format |
| `INBOX/` | Intake (L4) | Raw seed material (emptied on ingestion) |
| `knowledge/raw/` | Factory (L3) | Archived raw sources + derived `manifest.jsonl` |
| `knowledge/corpus/` | Source of truth (L3) | Canonical markdown chunks (`NN_slug.md`) |
| `knowledge/graph/` | Derived brain (L3) | FTS5 graph database, digest, and query tools |
| `knowledge/topics.md` | Controlled vocabulary | Registered topic tags for routing |
| `stages/` | Stage contracts (L2) | Contracts for phases `00_expand` through `05_evict` |
| `pipeline/` | Pipeline workflow | Global ordered plan `pipeline/WORKFLOW.md` |
| `reflection/` | Product (L4) | Generated `digests/`, `candidates/`, and `memory.md` |
| `scripts/` | Verification & tooling | Phase gates, manifest checks, eviction, promotion |
| `skills/` | Skills catalog (L1) | Reusable agent workflow packages; see `skills/SKILLS.md` |

## Route table by intent

| Intent | Where It Routes |
|---|---|
| Ingest new material / raw sources | `INBOX/` → `scripts/ingest.py` |
| Expand knowledge via web research | `scripts/expand_topic.py` → `INBOX/` |
| Query knowledge graph / brain | `knowledge/graph/ask.py` |
| Rebuild knowledge graph | `knowledge/graph/build_graph.py` |
| Run isolated reflection on topic | `pipeline/06_reflect/spawn.py --topic <slug>` |
| Promote / evict memory candidates | `scripts/promote_candidate.py` / `scripts/evict_stale.py` |
| Run pipeline gates & audit | `scripts/check_*.py` and `scripts/audit_workspace.py` |

## Common tasks

- **Broaden knowledge via web:** Run `python scripts/expand_topic.py "<topic>" [--tags t1,t2]` to deposit research notes into `INBOX/`.
- **Find & load a skill:** Check `skills/SKILLS.md` for task routing, then read `skills/<name>/SKILL.md`. Verify with `python skills/verify_catalog.py`.
- **Ingest new material:** Put raw files into `INBOX/`, then run `python scripts/ingest.py`.
- **Rebuild graph:** `python knowledge/graph/build_graph.py`.
- **Query the brain:** `python knowledge/graph/ask.py "<question>"` or with `--tag <t>`.
- **Verify pipeline gates:**
  - `python scripts/check_stage_contracts.py` (L2 contracts valid)
  - `python scripts/check_manifest.py` (Phase 1/2 intake & provenance)
  - `python knowledge/graph/watch.py --once` (Phase 3 graph consistency)
  - `python scripts/check_reflection.py` (Phase 4 reflection & citations)
  - `python scripts/check_reachability.py` (Phase 4 query reachability)
  - `python scripts/check_promotion.py` (Phase 5 promoted memory landing)
  - `python scripts/check_eviction.py` (Phase 5 grounded eviction)
- **Spawn reflection:** `python pipeline/06_reflect/spawn.py --topic <topic-slug>`
