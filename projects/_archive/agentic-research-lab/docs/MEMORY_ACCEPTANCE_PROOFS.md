---
type: Concept
title: MEMORY_ACCEPTANCE_PROOFS
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# Acceptance Proofs

The reproducible proof runner is:

```text
python scripts/prove_memory_system.py
```

It uses temporary source stores and does not mutate repository data. It currently proves these observable contracts:

| Proof | Result | Evidence |
|---|---|---|
| Secret redaction | PASS | Secret value absent from authoritative event payload |
| Projection rebuild/count preservation | PASS | 2 sessions, 1 event, 2 artifacts projected |
| Workspace isolation | PASS | Workspace one artifact selected; workspace two artifact excluded |
| Context budget | PASS | Estimated packet cost 556 <= fast budget 800 |
| Retention authorization | PASS | Unauthorized cleanup rejected; authorized cleanup removed only the eligible artifact |
| Session preservation | PASS | Session event remained after artifact cleanup |
| Frontier integrity | PASS | Valid empty frontier admitted with integrity `valid` |
| Promoted lesson retrieval | PASS | Accepted lesson admitted into deep context |
| MCP protocol envelope and context call | PASS | `initialize`, `tools/list`, and `get_context_packet` JSON-RPC contracts passed |
| Session hash-chain integrity | PASS | Two-event chain verified with `verify_chain` |
| Sensitive-path rejection | PASS | `.env` artifact rejected before persistence |
| Deterministic projection rebuild | PASS | Source fingerprint and counts identical across two clean projections |
| Invalid frontier fail-closed behavior | PASS | Canonical validation failure produced a diagnostic and withheld frontier records |
| Canonical frontier validation agreement | PASS | Gateway consumes `frontier_state.load_ledger`, `validate_ledger`, and `validate_manifest` |

These are acceptance proofs for the foundation, not proofs of retrieval superiority, production-scale performance, tokenizer-accurate cost, or complete MCP client interoperability.

The output includes generated artifact IDs and measured packet cost. Re-run the command to reproduce the checks against fresh temporary stores.
