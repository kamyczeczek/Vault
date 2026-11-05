---
type: Concept
title: UNIVERSAL_PROJECT_BRIDGE
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Recipe: Universal Cross-Project Bridge (`BRIDGE PROJECT <path>`)

**Trigger Phrase:** `BRIDGE PROJECT <path>` (e.g., `BRIDGE PROJECT C:\Users\Mateusz\Desktop\PROJECTS\ts-diverse`)

Use this universal workflow when you want to audit, reflect upon, and improve **any** external project using the knowledge graph and research methodologies of `agentic-research-lab`.

---

## 5-Step Execution Workflow

### Step 1: External Target Audit (`<path>`)
- **Action:** Inspect the workspace structure, package configuration, test suites, and recent error logs in the target project path.
- **Goal:** Identify bottlenecks, code quality issues, failing tests, or architectural debt.

### Step 2: Knowledge Graph Retrieval (`agentic-research-lab`)
- **Action:** Query our local FTS5 graph brain (`knowledge/graph/ask.py`) for relevant engineering patterns (e.g., benchmark resilience, anti-drift patterns, modular composition, robust evaluation, context engineering).
- **Command:**
  ```bash
  python knowledge/graph/ask.py --tag <relevant-domain-tag> --limit 10
  ```

### Step 3: Synthesis & RPI Design Plan & Project Brain Sidecar
- **Action:**
  1. Bootstrap a portable project brain sidecar in the target repository:
     ```bash
     python scripts/bootstrap_project_brain.py <path>
     ```
  2. Draft a structured design plan (`project-upgrade-plan.md`) bridging lab insights to concrete refactoring or enhancement tasks.

### Step 4: Targeted Implementation & Verification
- **Action:** Implement fixes, modular wrappers, or robust evaluation checks directly in the target project and run local test suites to guarantee zero regression.

### Step 5: Cross-Project Reflection & Workspace Evolution Sync
- **Action:** Summarize lessons learned from the external project and reflect on **necessary improvements to our own workspace (`agentic-research-lab`)** according to our workspace building knowledge (e.g., empirical gating, artifact hygiene, toolchain hardening). Commit reflection digests and candidate JSONLs back into `reflection/digests/` and `reflection/candidates/`.
