---
type: Concept
grade: active
title: CLAUDE
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# CLAUDE.md — knowledge-retrieval

Quality of the read path against a knowledge graph: does a query return the passage
that answers it, with the evidence intact? Works on the graph
`../../_archive/agentic-research-lab` builds; the engine itself stays there so its 67 call
sites keep working.

## Where things live

| Path | Role | Description |
|---|---|---|
| `CLAUDE.md` | Catalog (L0) | This file |
| `CONTEXT.md` | Contract (L1) | The retrieval-quality problem, its metrics, its gates |
| `references/defect-classes.md` | Reference (L3) | The failure modes found so far, and the gate that catches each |
| `references/measurements.md` | Reference (L3) | Standing numbers: recall, precision, latency, and what retired them |
| `reports/` | Product (L4) | Investigation records for each measurement round |

## The boundary with agentic-research-lab

The engine is called from 67 places inside ARL — stage contracts, the pipeline
workflow, handoffs, and the ECC agent definitions. Moving it would rewrite all of
them for no gain. So:

| Concern | Home |
|---|---|
| `ask.py` — the query surface | `../../_archive/agentic-research-lab/knowledge/graph/` |
| `build_graph.py` — index construction | `../../_archive/agentic-research-lab/knowledge/graph/` |
| `context_gateway.py` — the token-budgeted read path | `../../_archive/agentic-research-lab/knowledge/graph/`, measured from here |
| `build_quarantine.py` — exclude damaged chunks | `../../_archive/agentic-research-lab/scripts/` |
| **Measuring whether retrieval is any good** | here |

This project is where the question "is retrieval working?" is asked and answered.
It owns the benchmark, the defect taxonomy, and the verdicts — not the code
under measurement.

## Route by intent

| Intent | Go to |
|---|---|
| Measure retrieval quality | `../../_archive/agentic-research-lab/knowledge/graph/run_retrieval_benchmark.py` |
| Understand the current numbers | `references/measurements.md` |
| Learn what breaks retrieval | `references/defect-classes.md` |
| Read a past investigation | `reports/` |
| Rebuild a damaged-chunk quarantine | `python ../../_archive/agentic-research-lab/scripts/build_quarantine.py` |
| Ask a question of the graph | `python ../../_archive/agentic-research-lab/knowledge/graph/ask.py "<question>"` |

## Rules

- **A metric that measures the annotation is retired, not tuned.** `mean_exact_recall`
  was retired for exactly this reason: three independent proofs showed it scored
  the gold labels, not the retriever. No ranking change could have fixed it.
- **A gate asserts a relational property, not a local one.** The graph broke six
  ways while 15 local-property gates passed continuously. Local assertions pass
  through relational failures.
- **Write down what a metric cannot see.** Every retired metric states why.
