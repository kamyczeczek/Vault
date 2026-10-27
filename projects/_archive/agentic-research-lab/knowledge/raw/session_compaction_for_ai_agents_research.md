---
type: Concept
source: "Research Synthesis: Session Compaction and Context Window Management for AI Agents"
title: session_compaction_for_ai_agents_research
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Research Report: How to Approach Compacting Sessions by AI Agents

As AI coding agents handle longer horizons, multi-turn tool calls, and complex codebases, managing the context window becomes critical. Unbounded conversation history leads to **context bloat, latency degradation, attention dilution (lost-in-the-middle phenomena), and exorbitant API costs**. However, naive session compaction (asking an LLM to summarize past chat history) introduces severe failure modes.

Below is an exhaustive research synthesis on why naive compaction fails and how to engineer robust, deterministic session compaction for AI agents.

---

## 1. The Core Failure Modes of Naive Compaction

1. **Compaction Variance:** Relying on LLM-generated summaries to compress chat history is non-deterministic. Across different compaction runs, the model drops different constraints, file paths, and edge-case decisions, making agent behavior unpredictable.
2. **Loss of Granular Fidelity:** Summaries blur exact code snippets, precise error stack traces, and exact tool output parameters into vague prose ("fixed some bugs in the compiler"). Once lost, the agent cannot self-correct without re-querying the environment.
3. **The Re-Orientation Cost:** The true failure mode of context management isn't just forgetting information—it's the massive token and reasoning overhead required for an agent (or human reviewer) to re-orient itself after context is cleared or summarized.

---

## 2. Architectural Principles for Robust Session Compaction

### Principle A: Externalized Bounded State over Growing Files
Instead of compressing the chat log into a summary, maintain an **external, structured state record** at the execution boundary (e.g., `task_plan.md`, `frontier.json`, or a Kanban ledger).
- **Rule:** The chat window is ephemeral; the external state file is canonical.
- When compaction is triggered, the agent does not summarize the chat; it flushes its current active frontier, verified constraints, and next actionable step into the persistent state file, then clears the chat window entirely.

### Principle B: Query Over Read (Deterministic Indices)
- **"Notes survive compaction losslessly; summaries do not."**
- Rather than stuffing full conversation history or bulky documentation into the prompt context, use deterministic retrieval (such as SQLite FTS5 graphs, tag-intersection routing, or local code search) to pull exact corpus chunks, ADRs, and file contents **on demand**.

### Principle C: Checkpoint-Driven Context Reset (Git as the Source of Truth)
- In advanced agentic workflows (like Matt Pocock's or Vibhav's), agents operate inside disposable branches or worktrees.
- When a task checkpoint is reached (e.g., vertical slice implemented and tested), the state is committed to Git, and the agent session is completely wiped. Resuming work relies entirely on reading the Git diff, the test runner results, and the external plan file.

### Principle D: Structured Turn DAGs
- Track multi-turn agent interactions as a **Directed Acyclic Graph (DAG) of turns** rather than a linear transcript. Each node in the DAG captures:
  - `session_id` & `turn_index`
  - Model requests & tool outputs (retained as references, not full text)
  - Verification results (pass/fail status of tests)
  - Active blocker / next action

---

## 3. Step-by-Step Workflow for Compacting an AI Agent Session

When a session reaches token budget thresholds or experiences reasoning degradation:

1. **Flush & Pre-Register State:**
   Instruct the agent to write out its exact current state to disk (`task_plan.md` or a frontier ledger), capturing completed tasks, failing tests, and the immediate next step.
2. **Hard Clear (Wipe Chat Transcript):**
   Discard the linear chat history entirely. Avoid lossy LLM summarization of the raw transcript.
3. **Re-Initialize from External Contract:**
   Start the new session by injecting *only* the invariant workspace contract (`CLAUDE.md`, `CONTEXT.md`), the external state file (`task_plan.md`), and targeted query results from the knowledge graph.
4. **Verify Liveness:**
   Require the agent to run a quick deterministic check (e.g., run test suite or check git status) to re-ground its state in the physical environment before taking new actions.

---

## Summary Matrix

| Compaction Approach | Reliability | Information Retention | Re-Orientation Cost |
|---|---|---|---|
| **Naive LLM Chat Summary** | Low (High variance) | Poor (Drops exact code/paths) | High (Vague prose confuses agent) |
| **Externalized Bounded State Files** | High (Deterministic) | Perfect (Exact task status & plans) | Low (Instant resumption from file) |
| **Query-on-Demand (Knowledge Graph)** | High (Reproducible) | Lossless (Exact corpus chunks) | Low (Deterministic tag routing) |
| **Git Commit + Workspace Reset** | Maximum (Hard boundary) | Physical (Actual code diff & tests) | Zero (Environment is the truth) |
