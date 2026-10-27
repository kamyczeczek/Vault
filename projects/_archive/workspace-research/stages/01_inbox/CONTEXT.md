---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Stage 01_inbox — Raw intake

Raw intake — the only entry for new knowledge. Mirrors the project INBOX/.

## Inputs
- `INBOX/`
- `knowledge/raw/`

## Outputs
- `INBOX empty`
- `raw archived`

## Invoke
```
python scripts/ingest.py
```

## Contract
- **Intake invariant (Rule 5):** `ingest.py` archives `INBOX/` → `knowledge/raw/` and
  rebuilds `knowledge/raw/manifest.jsonl` in the same run, so INBOX is never left
  populated and the manifest cannot drift from the corpus it indexes.
- **Manifest gate:** `python scripts/check_manifest.py` must exit 0 after intake.
- Determinism: run is a no-op if the corpus fingerprint is unchanged. Read it live from
  `knowledge/graph/.graph_fingerprint` (or `GRAPH-DIGEST.md` line 1) — the value is
  `0626262b2982` at the time of writing, but it moves on every corpus edit, so never
  hardcode it here; a stale hardcoded value silently makes this contract lie.
- This stage's CONTEXT.md is the Inputs Table — the single disclosure level (one-level progressive disclosure).

## Handoff
Next stage consumes Outputs above via its own Inputs Table. The `.graph_fingerprint` + `GRAPH-DIGEST.md` fingerprint is the explicit handoff artifact for stage 03.
