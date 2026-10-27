---
type: Concept
title: reflection-fastpath
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Wayfinder map: reflection fast path

## Destination
A production-ready reflection path that is faster than the current `omp` path while preserving graph grounding, provenance, candidate schema, and rollback to `spawn.py`.

## Notes
Use `skills/wayfinder` for decision-first planning and `skills/unlazy` for acceptance gates. No external issue tracker is configured, so this local Markdown map is the tracker artifact. The current direct OpenAI-compatible endpoint experiment is not yet accepted: it timed out or returned upstream/402 errors for several models.

## Decisions so far
- [Reflection fast path gates](../../GATES-reflection-fastpath.md): acceptance outcomes were written before further implementation.
- [Presearch retrieval](../../pipeline/06_reflect/presearch.py): parallel retrieval and fingerprint-keyed cache are implemented and tested; this is an enabling component, not yet the replacement reflection path.
- [Backend decision](reflection-fastpath-backend.md): open; direct endpoint must be benchmarked and made reliable before replacing `omp`.

## Frontier tickets
- [ ] Reflection fast-path backend decision — determine whether pi's model API, a configured local endpoint, or `omp` remains the execution backend. Must include latency, reliability, JSON support, and rollback.
- [ ] Evidence-packet contract — decide how many chunks/excerpts enter one model call and how claim citations map back to retrieved chunks.
- [ ] Integration and gate wiring — only after the backend and packet decisions are closed; then wire `spawn.py` behind an explicit feature flag and run all gates.

## Not yet specified
- Whether the model router should be configured through pi's native model selection or a project-owned HTTP client.
- Whether structured output should use provider JSON mode or robust Python extraction plus schema validation.

## Out of scope
- Removing `omp` before the replacement has passed the gates.
- Changing corpus tags or graph schema as part of this latency effort.
