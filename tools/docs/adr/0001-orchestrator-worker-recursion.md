# ADR 0001: Orchestrator Agent Contract & Worker Recursion Test

- **Status**: PENDING (Implementation pending verification of recursion E2E test passing)
- **Date**: 2026-11-03
- **Context**: The worker agent recursion test (worker -> worker -> worker returning GRANDCHILD-OK-7731) did not reach the requested literal. The observed failure was `401 invalid x-api-key` from the worker provider path (Opus 4.8 through the local proxy at `127.0.0.1:4000`), not evidence of a tool-scope omission or a depth cap. The E2E recursion result remains unconfirmed.
- **Decision**:
  1. Define an explicit orchestrator configuration (`tools/orchestrator.md`) with explicit tools: `read, grep, find, ls, bash, Agent, get_subagent_result` overriding the default worker contract.
  2. Record the outcome as `IMPLEMENTACJA: PENDING` until successful E2E recursion verification passes.
- **Consequences**: `tools/orchestrator.md` remains a hypothesis for a later retest after provider authentication is repaired. It must not be treated as proof that recursion is supported. `IMPLEMENTACJA: PENDING` remains in force.
