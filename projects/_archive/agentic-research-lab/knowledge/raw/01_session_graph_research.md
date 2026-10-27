---
type: Concept
id: 01_session_graph_research
title: "Representing Whole Agent Sessions in a Graph-Backed Knowledge System: Event Sourcing, Knowledge Graphs, Provenance, and SQLite/FTS5 Architectures"
source: "Agentic Research Lab Broad Investigation & Literature Synthesis"
tags: [agentic, graph-database, event-sourcing, provenance, sqlite, mcp, observability, reflection, memory]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Representing Whole Agent Sessions in a Graph-Backed Knowledge System

## 1. Executive Summary & Scope

Modern autonomous AI agents execute complex, multi-turn, stateful trajectories involving prompt formulations, tool invocations, environment feedbacks, intermediate reasoning steps, errors, self-corrections, and inter-agent delegation. Traditionally, these execution traces are treated as ephemeral conversational transcripts stored in flat JSON arrays or unstructured log files. This research investigation explores the architectural, theoretical, and practical implications of elevating **whole agent sessions into a first-class graph-backed knowledge system**.

By representing sessions as interconnected graphs of events, states, tools, and artifacts rather than isolated chat histories, systems can achieve:
1. **Time-travel debugging and session replay**: Instantly restoring or branching execution from any intermediate decision point.
2. **Unified episodic, semantic, and procedural memory**: Bridging raw execution traces (episodic) with extracted generalized rules (semantic) and executable workflows (procedural).
3. **Robust provenance tracking**: Establishing cryptographically sound or relational derivation chains (`prov:wasGeneratedBy`, `prov:wasDerivedFrom`) for every tool output and synthesized artifact.
4. **SQL-native and FTS5 queryability**: Enabling agents to query their own past session histories and workspace state using standard relational and full-text search primitives, as demonstrated by emerging production architectures (e.g., Lewis's SQL-centric agent context pattern).

This report synthesizes external literature, standards (W3C PROV, OpenTelemetry, Model Context Protocol), and database theory, contrasting them against the current `agentic-research-lab` repository architecture to identify novel, rigorous research directions.

---

## 2. Comparative Analysis: Repository Baseline vs. Session Graph Architecture

The current `agentic-research-lab` repository maintains a deterministic, scientific, graph-backed research lab governed by a strict 5-phase pipeline (`01_inbox` $\rightarrow$ `02_corpus` $\rightarrow$ `03_graph` $\rightarrow$ `04_reflect` $\rightarrow$ `05_evict`).

### Repository Baseline (`knowledge/graph/graph.db`):
- **Storage Model**: SQLite relational database with FTS5 virtual tables (`fts`, `fts_content`, etc.), node tables (`nodes`), and edge tables (`edges`).
- **Ingestion Path**: Markdown chunks (`knowledge/corpus/*.md`) $\rightarrow$ `build_graph.py` $\rightarrow$ SQLite nodes and typed relation edges (`derives_from`, `supports`, `refutes`, `contradicts`, `extends`, `shares_tag`).
- **Query Paradigm**: Hybrid BM25 full-text search combined with Reciprocal Rank Fusion (RRF) via `ask.py` and exposed to IDEs/clients via an MCP server (`knowledge/graph/mcp_server.py`).
- **Memory & Reflection**: Stored in `reflection/memory.md` (promoted rules adhering to canonical `Rule`/`Evidence`/`Target`/`Action` schemas) and tracked via JSONL candidate ledgers (`reflection/candidates/*.jsonl`).

### Limitations of the Static Corpus Model for Sessions:
While the repository excels at static document indexing and retrospective reflection, it lacks a native representation for **dynamic, interactive agent sessions**. Static corpus chunks capture *what is known*, but fail to capture *how an agent arrived at a conclusion* (the trial-and-error trajectory, intermediate tool failures, state mutations, and temporal ordering of actions).

Expanding the knowledge graph to encompass whole agent sessions bridges this gap, transforming the lab from a static document repository into a **self-reflective operating system where past executions are queryable memory**.

---

## 3. Technical Mechanisms & Literature Synthesis

### 3.1 Event Sourcing and Append-Only Logs for Agent Execution
- **Mechanism**: Rather than overwriting state tables or storing monolithic state blobs, agent sessions are modeled as an immutable append-only sequence of domain events (`SessionStarted`, `PromptSubmitted`, `ToolRequested`, `ToolExecuted`, `ErrorEncountered`, `StateMutated`, `SessionCompleted`).
- **State Derivation**: Current agent state at step $t$ is computed by left-folding the event stream $E_1, E_2, \dots, E_t$.
- **Benefits**: Complete auditability, zero data loss, effortless branching (forking an agent session from event $k$), and robust crash recovery.
- **External Evidence & Literature**: Event sourcing patterns in distributed systems (Martin Fowler, *Event Sourcing*; Greg Young) applied to LLM agent frameworks (e.g., LangGraph state persistence, Mastra workflow engines).

### 3.2 Knowledge Graphs for Episodic, Semantic, and Procedural Memory
Drawing from cognitive architectures (ACT-R, Clarion) and advanced agent memory frameworks (e.g., Generative Agents, ExpeL, MemGPT):
- **Episodic Memory**: Specific instances of agent sessions (`Session_42`: "Investigated test failure in `check_reflection.py` at timestamp $T$, invoked `pytest`, encountered assertion error, patched regex, verified green").
- **Semantic Memory**: Abstracted, context-free facts and rules stored in knowledge graph nodes (e.g., promoted rules in `reflection/memory.md`).
- **Procedural Memory**: Action sequences, tool invocation graphs, and parameterized workflows that successful agents execute to achieve goals.
- **Integration**: The session graph acts as the bridge where episodic logs are periodically mined by reflection agents to mint semantic rules and procedural templates.

### 3.3 Provenance and W3C PROV in Agentic Workflows
- **W3C PROV Standard**: Defines entities, activities, and agents. In an agent session graph:
  - **Entities**: Prompts, tool outputs, files, git commits, corpus chunks, intermediate JSON payloads.
  - **Activities**: Tool executions, LLM completion calls, reasoning loops, test runs.
  - **Agents**: LLM model instances, human operators, automated background watchdogs.
- **Derivation Edges**: `prov:wasGeneratedBy` (entity produced by activity), `prov:used` (activity consumed entity), `prov:wasDerivedFrom` (artifact $B$ derived from artifact $A$).
- **Value**: Eliminates ungrounded hallucinations by mathematically tracing any synthesized conclusion back through the exact prompt, tool output, and git commit history that generated it.

### 3.4 OpenTelemetry Tracing and Span/Event Models for AI Agents
- **Span-Event Hierarchy**: Adopting OpenTelemetry (OTel) semantics for AI agent workflows:
  - **Traces**: Represent entire agent sessions or multi-agent runs.
  - **Spans**: Represent discrete bounded operations (e.g., `LLM.completion`, `Tool.bash_execution`, `Graph.query`). Spans record start/end times, parent-child relationships, and metadata attributes (token counts, model names, latency).
  - **Events**: Structured logs within spans (e.g., raw tool stderr, truncation notices, retry attempts).
- **Mapping to Graphs**: OTel span trees map naturally to Directed Acyclic Graphs (DAGs) stored in SQLite, allowing SQL queries over execution performance, token economics, and error hotspots.

### 3.5 Agent Client Protocol (MCP) Session/Event Models
- **MCP & ACP Protocols**: Model Context Protocol (MCP) and Agent Client Protocol standardize how agents interact with tools, resources, and clients.
- **Session Lifecycles**: MCP sessions maintain state boundaries across client connections. Representing MCP tool call requests and JSON-RPC message exchanges as graph nodes enables auditing external tool interactions, tracking rate limits, and caching deterministic tool results.

### 3.6 Graph Databases vs. Relational/Event Stores for Agent Sessions
- **Property Graphs vs. RDF vs. Relational (SQLite)**:
  - *Property Graphs* (Neo4j, NebulaGraph) offer native traversal APIs (`MATCH (s:Session)-[:EXECUTED]->(t:ToolCall)`) but introduce heavy operational overhead and server-based infrastructure.
  - *Relational/Event Stores with SQLite* (FTS5 + JSON1 + Adjacency Lists) provide zero-dependency local execution, atomic ACID transactions, file portability, and exceptional performance for embedded agents, matching this repository's minimalist philosophy.
- **SQLite Viability**: With SQLite's `json_each()`, recursive CTEs (`WITH RECURSIVE`), and FTS5 full-text indexing, complex graph traversals and session replays can be executed locally with zero external daemons.

### 3.7 Temporal and Property Graphs in Autonomous Systems
- **Bitemporal Modeling**: Tracking two time axes:
  1. *Valid Time*: When an agent belief or fact was true in the task environment.
  2. *Transaction Time*: When the agent recorded the event in the session knowledge store.
- **Property Graph Schema**: Nodes carry attributes (properties) and timestamps. Edges represent temporal succession (`NEXT_EVENT`), causality (`CAUSES`), and hierarchical containment (`CONTAINS_TURN`).

### 3.8 Session Replay, Observability, and Deterministic Debugging
- **Post-Mortem Analysis**: Non-deterministic LLM behavior makes debugging difficult. A graph-backed session log allows developers and meta-agents to "rewind" to event $T_{15}$, modify the system prompt or tool output, and execute a counterfactual replay (`branch session`).
- **Observability Metrics**: Querying session graphs for tool failure rates, average reasoning steps per success, and token consumption bottlenecks.

### 3.9 Privacy, Redaction, Retention, and Provenance Governance
- **Challenges**: Agent sessions frequently ingest sensitive data, API keys, PII, or proprietary code.
- **Architectural Solutions**:
  - *Redaction Filters*: Intercepting tool outputs and prompts at the logging boundary (pre-commit / pre-ingest hooks) to sanitize secrets.
  - *Tiered Retention*: Evicting raw ephemeral episodic logs after successful semantic distillation (aligning with phase 5 eviction contracts), while retaining distilled knowledge.
  - *Cryptographic Hashing*: Hashing sensitive payload content in public logs while storing pointers to encrypted vault storage.

### 3.10 Agent Reflection, Experience Replay, and Generalization (ExpeL, LEMA)
- **Literature**: ExpeL (Experience Learning) and LEMA (Learning from Mistakes) demonstrate that LLM agents improve significantly when they extract generalized principles from past failure trajectories rather than memorizing raw chat logs.
- **Graph Integration**: Session graphs provide the granular training data (failures, error messages, correct fixes) required for automated reflection engines to mint high-quality candidates for `reflection/memory.md`.

### 3.11 Practical SQLite/FTS5 Designs for Session Graphs
An efficient, zero-dependency SQLite schema for session graph storage:
```sql
-- Core session metadata
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    status TEXT CHECK(status IN ('active', 'completed', 'failed', 'branched')),
    metadata TEXT -- JSON blob
);

-- Immutable event log (Append-only / Event Sourcing)
CREATE TABLE session_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT REFERENCES sessions(session_id),
    parent_event_id INTEGER REFERENCES session_events(event_id),
    sequence_num INTEGER NOT NULL,
    event_type TEXT NOT NULL, -- PROMPT, TOOL_CALL, TOOL_RESULT, ERROR, LLM_RESPONSE
    actor TEXT NOT NULL,
    payload TEXT NOT NULL, -- JSON payload
    created_at TEXT NOT NULL
);

-- Graph edges between events/artifacts
CREATE TABLE session_edges (
    source_id INTEGER REFERENCES session_events(event_id),
    target_id INTEGER REFERENCES session_events(event_id),
    relation TEXT NOT NULL -- DERIVES_FROM, CAUSES, FOLLOWS, REFUTES
);

-- FTS5 full-text index on event payloads and prompts
CREATE VIRTUAL TABLE session_fts USING fts5(
    event_id UNINDEXED,
    session_id UNINDEXED,
    content,
    tokenize='porter unicode61'
);
```

---

## 4. Alternatives, Limitations, and Threat Models

1. **Context Window Bloat**: Ingesting entire session histories directly into agent context windows causes rapid degradation and high token costs. *Mitigation*: Query-time retrieval via SQLite FTS5 / RRF (analogous to `ask.py`) and hierarchical summarization.
2. **State Explosion & DB Bloat**: Long-running agent sessions generate millions of events. *Mitigation*: Automated retention policies, snapshotting state at key checkpoints, and evicting transient tool output logs.
3. **Circular Provenance & Hallucinated Derivations**: Agents might create invalid dependency edges. *Mitigation*: Strict graph validation gates (similar to `check_reflection.py` and `check_eviction.py`).
4. **Security Boundaries**: Giving agents arbitrary SQL access to session stores introduces SQL injection or data leakage risks. *Mitigation*: Read-only database roles, parameterized queries, and scoped views (as practiced in Lewis's Conductor API pattern).

---

## 5. Concrete Research Questions for Lab Validation

To operationalize these insights within the `agentic-research-lab` framework, the following testable hypotheses are proposed:
1. **Hypothesis Q1 (Session-Backed Reflection Quality)**: Mining reflection candidates from structured SQLite session graphs rather than unstructured flat-file transcripts increases the proportion of promoted rules passing validation (`check_promotion.py`) by $\ge 30\%$.
2. **Hypothesis Q2 (SQL Context Retrieval Efficiency)**: Equipping agents with a SQL/FTS5 session query tool reduces redundant tool calls during complex debugging tasks by $\ge 40\%$ compared to keyword grep or full-file reading.
3. **Hypothesis Q3 (Counterfactual Replay Success)**: Branching execution from an intermediate session event node enables automated self-correction of failed agent runs with a success rate exceeding $65\%$.

---

## 6. Epistemic Classification: Facts, Evidence, Hypotheses, and Recommendations

### Verified Facts
- SQLite supports robust ACID transactions, recursive CTEs, JSON1 functions, and FTS5 full-text search, making it a viable embedded graph store.
- W3C PROV and OpenTelemetry provide standardized conceptual frameworks for provenance and span/event tracing.
- Unstructured chat history management leads to context rot and loss of intermediate reasoning traces in long-running agent sessions.

### External Evidence & Citations
- **ExpeL / LEMA**: Experience-based learning from agent mistakes improves reasoning performance.
- **Lewis (Conductor / YC DB)**: "The unreasonable effectiveness of putting everything in a database and handing your agents a SQL tool" (Conductor API case study, 2025/2026).
- **W3C PROV Recommendation**: Provenance data model for Web architecture.
- **OpenTelemetry Trace Specification**: Distributed tracing spans and events.

### Hypotheses
- Session graphs queried via SQL/FTS5 will outperform vector RAG for precise retrieval of past agent tool interactions and code edits.
- Automated provenance tracking will reduce ungrounded hallucination rates in reflection memory.

### Recommendations for Repository Evolution
1. **Do not modify existing core graph structures (`graph.db`)** during initial research phases; instead, prototype session event logging in isolated SQLite test databases.
2. **Implement event-sourcing wrappers** around agent tool execution loops to capture structured telemetry.
3. **Incorporate session query capabilities** into MCP server tools (`knowledge/graph/mcp_server.py`) to allow external agents to inspect historical session trajectories.
