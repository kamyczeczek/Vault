---
type: Concept
title: START-HERE
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# START-HERE.md — agentic-research-lab

You are looking at a deterministic, graph-backed scientific knowledge lab for researching **how to do agentic research well**.

## The Core Loop

1. **Investigate & Fetch (`00_expand`):** Extract primary scientific literature on agent autonomy, planning, multi-agent debate, hallucination reduction, and literature synthesis.
2. **Standardize & Ingest (`01_inbox` & `02_corpus`):** Turn papers into atomic frontmatter markdown chunks.
3. **Graph Brain (`03_graph`):** Index corpus into FTS5 SQLite graph with BM25 retrieval and tag links.
4. **Reflect & Synthesize (`04_reflect`):** Spawned agents synthesize cross-paper patterns and propose concrete rules.
5. **Evict & Promote (`05_evict`):** Re-test candidates against live graph nodes. Promote verified best practices to `reflection/memory.md`.
6. **Meta-Evolve (`06_meta_evolve`):** Apply validated insights back into the workspace's own stage contracts and instructions.

## Key Invariants

- **Knowledge as files:** Findings are canonical markdown chunks; the graph is a derived index.
- **Evidence-grounded:** No reflection candidate exists without resolvable chunk citations.
- **Self-Improving:** Research on researching directly modifies and sharpens the research lab.
- **Clean intake:** `INBOX/` must be emptied on ingestion.

## How to Query & Run

```bash
# Query the knowledge graph
python knowledge/graph/ask.py "how do agents reduce hallucination in literature synthesis"

# Rebuild the graph
python knowledge/graph/build_graph.py

# Spawn reflection on a topic
python pipeline/06_reflect/spawn.py --topic scientific-discovery

# Check system health
python scripts/audit_workspace.py

# Apply learned lessons to workflow
python scripts/apply_meta_learning.py
```

## Quality & Git Workflow

```bash
# Complete read-only quality audit
python scripts/quality_check.py

# Safe, gated Git checkpoint (strictly explicit staging, full gate verified)
python scripts/agent_commit.py --scope 03_graph --message "rebuild knowledge graph for newly ingested literature" --stage knowledge/graph/.graph_fingerprint knowledge/graph/GRAPH-DIGEST.md

# Create isolated agent worktree for parallel work
python scripts/git_worktree.py create --name subagent-analysis

# Guarded non-destructive revert of a bad commit
python scripts/git_rollback.py revert --commit <hash>

# Preview intake without modifying INBOX, corpus, or raw archives
python scripts/ingest.py --dry-run
```
