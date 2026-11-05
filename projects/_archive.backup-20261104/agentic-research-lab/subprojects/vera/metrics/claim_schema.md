---
type: Concept
title: claim_schema
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Claim Schema (unit of VERA evaluation)

One JSONL row per claim in `runs/<qid>_<EXP>_claims.jsonl`.

## Fields

| Field | Type | Required | Rule |
|---|---|---|---|
| claim_id | string | yes | `<qid>_<EXP>_c<NN>` |
| statement | string | yes | one sentence, testable |
| source_ids | [string] | yes | chunk IDs; `[]` allowed ONLY if support_type=novel and novelty_reason set |
| support_type | enum | yes | `direct` \| `inferred` \| `contradictory` \| `novel` |
| confidence | enum | yes | `high` \| `medium` \| `low` |
| mechanism | string | yes for high/medium | primitive + condition that makes the claim true; skeletal, not prose-summary |
| limitation | string | yes | boundary where the claim stops holding |
| verification_status | enum | yes | `unverified` \| `grounded` \| `falsified` \| `needs_probe` — set only by tooling, never by the synthesizer |

## Addendum (2026-09-24, from first B0.1 runs)

- `source_ids` may contain a **workspace source** prefixed `workspace:<file>` (e.g.
  `workspace:CONTEXT.md`, `workspace:stages/05_evict/CONTEXT.md`,
  `workspace:reflection/memory.md`). A `direct` claim citing only workspace sources sets
  `source_ids` to those prefixed entries — empty `source_ids` is reserved for `novel`.
- Recall scoring (scorecard dim 1) counts workspace sources separately from corpus recall.

## Invariants

1. Every `direct` claim with ≥1 source_ids must pass ask.py resolution before the run may close
   (verification_status=grounded); unresolved ⇒ the claim row is invalid, run re-opens.
2. `contradictory` claims must name the opposing chunk ID in source_ids too.
3. `novel` claims (agent-originated) are allowed in sections 11 (proposed experiments) only —
   novelty inside sections 5–9 without sources is defect type D5 in the injection test.
4. statement is hash-normalized for reproducibility: lowercase, whitespace-collapsed; hash =
   sha256(statement|support_type|mechanism).

## Sample row

```json
{"claim_id":"Q5_B0_c03","statement":"promotion requires at least two resolvable chunk citations","source_ids":["03_graph_X","05_evict_Y"],"support_type":"direct","confidence":"high","mechanism":"05_evict gate re-tests candidate against live graph nodes before writing to memory.md","limitation":"does not apply to in-candidate experimental rules","verification_status":"grounded"}
```
