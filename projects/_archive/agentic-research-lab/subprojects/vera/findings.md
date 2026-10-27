---
type: Concept
title: findings
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Findings: VERA Phase 1 setup

## Research date: 2026-09-24
## Researcher: Goose (Sapiens AI)

## Key decisions

1. **Claim-level evaluation** — the unit of scoring is a claim (claim_schema.md), not a document. Rationale: polished narratives are unmeasurable; claims are falsifiable.
2. **Hard experiment ordering** — A(query decomposition) → B(iterative retrieval) → C(graph edges) → E(verification, flagship) → D(skeletal) → reproducibility → F(debate, gated). Rationale: F after E so we don't debate on top of an unverified base.
3. **Frozen corpus** — fingerprint pinned at first B0 run; no ingestion during study. Rationale: corpus drift invalidates seed annotations and cost curves.
4. **Instrument over lab** — all VERA metric tooling lives under subprojects/vera/; workspace code is read-only input. Rationale: experiments must not mutate the system under test mid-study.
5. **Injection test as research instrument** — the existing quality gates become measurable: 5×5 gate×defect detection matrix replaces "gates pass" with "gate X catches defect Y at rate Z for cost C".

## Open (fog)

- Benchmark leak risk: LLMs may know public literature behind L5 questions — needs outside-workspace question set if L5 variance is too low.
- Debate experiment F: only if E shows single verified agent is the ceiling.
- Cost budget: set once B0 cost curve exists.
