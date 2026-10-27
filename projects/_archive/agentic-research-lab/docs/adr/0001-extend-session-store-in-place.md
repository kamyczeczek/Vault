---
type: Concept
title: 0001-extend-session-store-in-place
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Extend session_store in place rather than founding a conversation project

The workspace had a hash-chained conversation ledger
(`knowledge/graph/session_store.py`) that nothing wrote to, and a request for a
knowledge brain that could converse, record, and produce future insight. Rather
than open a new project for the conversation side, the recorder was added next
to the ledger it feeds. Root decision D13 makes expansion a last resort — the
risk is unverified composition, not too few projects — and the composed option
was verified before the fork was taken: the ledger recorded a real session,
verified its chain, and redacted a planted secret.

## Considered Options

- **New project consuming the ledger as a contract.** Would have needed
  `session_store` to gain a documented public API, adding a project and a
  contract to express something two files already express.
- **Moving the ledger to a new project.** Cleanest subject boundary — a daily
  conversation brain is not research — but `tests/test_session_store_policy.py`,
  `scripts/prove_memory_system.py`, and the MCP server all import it from
  `knowledge.graph`. A move breaks three call sites to relocate one file.
- **Extend in place (chosen).** One ledger, one owner, one import path.

## Consequences

The conversation ledger's home is a research project. A reader looking for
"where do conversations get recorded" will look in a research repository, which
is mildly misleading. The mitigating cost is one file, and the alternative was
three broken call sites.

`record_turn.py` pins a closed event vocabulary that `session_store.append_event`
deliberately does not: the library stays open for its own tests and the MCP
server, while the recorder refuses drift for callers that must stay searchable.
If a second consumer ever needs a type outside the eight, the vocabulary grows
there rather than in the library.
