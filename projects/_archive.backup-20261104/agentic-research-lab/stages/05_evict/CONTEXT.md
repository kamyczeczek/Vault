---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Stage 05_evict — Candidate Eviction & Grounding Maintenance

## Inputs
- `reflection/candidates/*.jsonl`
- `knowledge/graph/graph.db`
- `knowledge/graph/.graph_fingerprint`
- `reflection/memory.md`

## Process
1. Load active heuristics: `python scripts/apply_rules.py --task "eviction maintenance and meta-learning evolution" --format prompt`
2. Inspect candidate claims against active nodes in `graph.db`.
3. Run `python scripts/evict_stale.py` to identify candidates citing missing/evicted graph chunk IDs.
4. Record eviction entries in `reflection/evictions/<run>.jsonl` with an auditable `why`.
5. Validate promotions land on the read path via `python scripts/check_promotion.py`.
6. Apply accepted rules to evolve stage contracts and workflows: `python scripts/apply_meta_learning.py`.
## Side-effect verification contract
- Every state-changing action must record the expected postcondition and verify it independently before the phase can pass.
- Agent-reported success is not evidence; use artifact hashes, graph fingerprints, manifest reconciliation, or downstream state queries.
- A missing verifier is a failed prerequisite, not permission to use a weaker fallback.

## Outputs
- `reflection/evictions/*.jsonl`
- Updated candidate states (`rejected`)

## Exit Gate
- Every rejected candidate carries an auditable non-empty `why`.
- Rejections strictly cite IDs that no longer resolve in `graph.db`.
- `python scripts/check_eviction.py` exits 0.
- `python scripts/check_promotion.py` exits 0.
- `python scripts/apply_meta_learning.py --dry-run` exits 0 (ensures the meta-learning pipeline is functional).
## Bounded execution policy
- Agent loops must declare maximum steps, retries, delegation depth, and wall-clock budget.
- Repeated identical actions without state progress must terminate and escalate.
- External publication, deployment, deletion, credential use, and network writes require explicit approval or a deterministic allowlist.
