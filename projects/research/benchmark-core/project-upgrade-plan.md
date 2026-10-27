---
type: Concept
title: project-upgrade-plan
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# Project Upgrade Plan: the workspace bridge (originally `ts-diverse`)

## Executive Summary
This upgrade plan bridges the advanced research methodologies, context engineering principles (ICM), and token efficiency rules (`The Goose Principle`) of `agentic-research-lab` into the forecasting projects.

---

## 1. Objectives & Improvements

### A. Context Hygiene & Token Efficiency (The Goose Principle)
- **Problem:** When mutating time-series models or running ablation sweeps (`mutation_engine.py`, `bench.py`), agents frequently waste thousands of tokens inspecting large script outputs or full module files.
- **Solution:** Enforce AST-level retrieval and explicit 2-action persistence. Stop iteration immediately upon encountering repeated errors (*Fail Fast & Cheap*).

### B. Project Brain Sidecar Integration (`.brain`)
- **Status:** Successfully bootstrapped `.brain/` with 88 corpus chunks and an FTS5 SQLite index (`graph.db`).
- **Action:** Agents operating in this project will now load context directly from `.brain/graph/GRAPH-DIGEST.md` rather than crawling raw files.

### C. Deterministic Evaluation Gating
- **Action:** Ensure all mutation and benchmarking runs are gated through strict validation scripts (e.g., `check_bench.py`) before promotion, preventing regression on SOTA sunspot, chaos, and financial tasks.

---

## 2. Action Items

1. **Create root `CLAUDE.md` and `CONTEXT.md`**: Standardize entry routing and ICM layer contracts.
2. **Wire Quality Gates**: Bind benchmark evaluation runs to mandatory exit-code verification.
3. **Execute & Verify**: Run benchmark harness verification to ensure 0 regression.
