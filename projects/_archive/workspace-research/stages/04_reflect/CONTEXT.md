---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Stage 04_reflect — Isolated reflection. Reads graph via ask.py --tag, writes reflection/ only. Determinism gated.

Isolated reflection. Reads graph via ask.py --tag, writes reflection/ only. P1 plan phase, P2 ADAPT, P3 compaction guard apply.

## Inputs (allowed — P4 tightening)
- `knowledge/graph/graph.db` (derived, `.graph_fingerprint` gated)
- `knowledge/graph/GRAPH-DIGEST.md` (auto-injected; P3 re-injection source every N calls)
- `knowledge/topics.md` (controlled vocabulary; flat aliases `decomposition/htn/pddl/classical-planning` per P6)
- `reflection/memory.md` (promoted accepted rules; the read half of the promotion loop —
  written by `scripts/promote_candidate.py`, gated by `scripts/check_promotion.py`)
- Allowed tag intersections per topic (P4): `icm+planning`, `icm+reflection`, `context-engineering+reflection`, `context-engineering+memory`, `planning+decomposition`, `planning+world-models` (empty is valid — signals vocabulary gap), and `planning+htn/pddl/classical-planning` alias expansion via `route.py --threshold`.

## Outputs
- `reflection/digests/<topic>.md` (Claim/Evidence/Decision/Next bet; provenance stamp `fingerprint + plan_version + phase + routing` per P5)
- `reflection/candidates/<topic>.jsonl` (state machine; provenance object per P5)

## Invoke (P1 ordered)
```bash
python knowledge/graph/watch.py --once            # determinism gate (refuse STALE_DIGEST)
python pipeline/06_reflect/route.py --tag <t> [--threshold 3]  # P2 one-level split if card<threshold
python pipeline/06_reflect/spawn.py --topic <slug>             # enforces WORKFLOW.md + fingerprint + phase stamp
python scripts/check_reflection.py               # exit gate
python scripts/check_promotion.py             # sub-gate: accepted rules landed on the read path
```

## Contract
- Determinism: hash-gated on `knowledge/graph/.graph_fingerprint` +
  `pipeline/WORKFLOW.md` sha12. `spawn.py` refuses if either is missing/mismatched.
  Both values move on every corpus/plan edit — read them live from those two files
  at gate time; never hardcode either value here, or this contract silently describes
  a graph that no longer exists.
- Single disclosure level (one-level progressive disclosure; P2/P6 — no recursive expansion).
- Every claim cites ≥1 `ask.py --tag` id; missing citation ⇒ rejected (gate).
- Provenance: each digest/candidate embeds `fingerprint + plan_version + phase + routing queries`; missing ⇒ gate failure (P5).
- P3: agent re-anchors to this Inputs Table + current WORKFLOW phase header on compaction/every N calls.

## Handoff
Next consumer is not a stage (this is terminal). The `reflection/digests/*.md` + `candidates/*.jsonl` provenance is the handoff to promotion (`scripts/promote_candidate.py`) and to `scripts/check_reflection.py`/`review_gate.py` observability. The `.graph_fingerprint` + `GRAPH-DIGEST.md` fingerprint is the explicit handoff from stage 03.
