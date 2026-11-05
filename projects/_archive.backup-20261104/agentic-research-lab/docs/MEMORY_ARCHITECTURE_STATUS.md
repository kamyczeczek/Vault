---
type: Concept
title: MEMORY_ARCHITECTURE_STATUS
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# Workspace Memory Architecture Status

## Status

**Validated research prototype, not production-complete.**

The workspace-memory system is an executable architecture experiment. It is intentionally composed from small, inspectable primitives rather than presented as a finished general-purpose memory product.

The current implementation has a tested foundation for corpus retrieval, session projection, frontier-aware context, privacy filtering, retention planning, and bounded context packets. Passing tests establish local contracts. They do not establish production readiness, retrieval superiority, or end-to-end MCP compatibility.

## Why we are building this instead of adopting one memory product

The experiment combines constraints that are not necessarily co-optimized by an existing memory or graph product:

- authoritative corpus, session, frontier, artifact, and lesson stores remain separate;
- derived retrieval projections must be disposable and rebuildable;
- provenance and integrity must remain visible;
- sensitive paths and secret-like payloads must be excluded or redacted;
- retention and destructive cleanup require explicit policy boundaries;
- retrieval must be workspace-scoped and bounded for low-token agent use;
- the system must remain inspectable and usable with local files and SQLite.

These reasons justify exploring a custom composition layer. They do not justify assuming that every custom helper is better than an existing implementation.

## Reinvention register

| Component | Existing alternative or owner | Why this prototype exists | Source of truth | Success evidence | Reversibility |
|---|---|---|---|---|---|
| Session projection | SQLite queries, generic event stores, graph databases | Test whether a disposable graph-oriented projection improves session retrieval while preserving an append-only store | `knowledge/graph/sessions.db` | Rebuild/count/integrity tests; retrieval quality still unmeasured at representative scale | Delete and rebuild `session_graph.db` |
| Unified context gateway | Agent-memory frameworks, vector stores, direct tool calls | Test bounded composition of corpus, session, frontier, artifact, and lesson evidence | Each underlying authoritative store | 45 local tests; task-success and latency evaluation still required | Remove gateway; source stores remain usable |
| Frontier-aware retrieval | `scripts/frontier_state.py` and `scripts/check_frontier.py` | Make continuation state available in bounded context without copying it into the corpus graph | `frontier/ledger.jsonl` plus `manifest.json` | Integrity-aware and fail-closed tests; all readers share `frontier_state.inspect_frontier`, and agreement with `status()` is pinned | Disable source adapter; frontier files remain authoritative |
| Artifact policy | Filesystem and database ACLs, retention services | Encode workspace-specific exclusion, redaction, retention, and explicit cleanup boundaries | Session store metadata plus original files | Policy and workspace-isolation tests; full deletion audit workflow remains incomplete | Artifact metadata is removable; source files are not touched by cleanup |
| Promoted lesson retrieval | `scripts/apply_rules.py` parser and `reflection/memory.md` | Test whether accepted lessons improve contextual continuity | `reflection/memory.md` | Lexical matching tests; `scripts/memory_rules.py` is the one accepted-rule parser for both application and meta-learning; relevance evaluation remains required | Disable lesson adapter; memory file remains intact |
| Budget packing | Model-specific tokenizers and orchestration frameworks | Provide a cheap deterministic bound before a target tokenizer is selected | Gateway candidate text | Budget tests; estimates are character-based, not tokenizer-accurate | Replace estimator without changing source stores |

## Adoption gates

A component may move beyond prototype status only when its benefit is demonstrated against a representative baseline.

### Gateway

- Compare unified packets against individual source tools.
- Measure task continuation success, supported-answer rate, latency, and estimated context cost.
- Include negative cases where invalid frontier state must not influence context.

### Session projection

- Verify deterministic rebuild equivalence from a clean projection.
- Measure query latency and retrieval quality against authoritative-store queries.
- Confirm workspace isolation and provenance preservation on realistic data.

### Frontier adapter

- ~~Reuse the canonical frontier validator rather than maintaining a second semantic validator.~~ Done: `check_frontier.py` and the gateway both call `frontier_state.inspect_frontier`.
- ~~Prove that valid retrieval state agrees with `frontier_state.status()` and `check_frontier.py`.~~ Done: `tests/test_consolidation.py::FrontierInspectorTests` pins agreement on valid, half-written, and stale-manifest frontiers.
- Keep invalid and partial state fail-closed by default; forensic access must remain explicit.

### Lesson adapter

- ~~Share the canonical accepted-rule parser with rule application.~~ Done: `apply_rules.py` and `apply_meta_learning.py` both parse through `scripts/memory_rules.py`; consumer agreement is pinned in `tests/test_consolidation.py`.
- Evaluate whether retrieved lessons improve outcomes without increasing irrelevant context.

### Retention policy

- Define expiry semantics, audit records, recovery expectations, and authorization boundaries.
- Test deletion against realistic multi-workspace data before claiming lifecycle completeness.

## Engineering rules for future changes

Before adding a subsystem or helper, record:

1. Existing alternatives and repository owners.
2. The specific gap that motivates custom behavior.
3. The hypothesis being tested.
4. The success metric and baseline.
5. The authoritative source of truth.
6. The reversibility or removal plan.

Do not convert a passing synthetic test into a production claim. Do not duplicate validation or parsing rules when an authoritative subsystem already owns them. Prefer adapters around canonical sources and rebuildable projections over additional stores.

## Current limitations

- The gateway uses approximate character-based token estimates.
- Frontier matching is lexical and currently has a duplicated integrity adapter that should be consolidated with the canonical frontier validator.
- Artifact retrieval returns metadata rather than artifact contents.
- Lesson matching should share the canonical rule parser.
- MCP exposes the normal context path, but end-to-end MCP invocation and forensic frontier controls need separate validation.
- The working tree contains broad unrelated changes and generated artifacts that must be isolated before a trustworthy release commit.
- The agentmemory capture layer (external engine on :3111) silently no-ops its LLM distillation when the configured model is not served by the router (scar 2026-09-30: `success:true` with empty results while the circuit was open). `preflight.py` now probes the router model list + engine at session start; `scripts/close_session.py` closes the session→`.md`→consolidate→gate loop; `EXPERIENCE.md` is the stack runbook.
