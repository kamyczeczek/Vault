---
type: Concept
id: 00_icm_map
title: "ICM_map.md (part 1/3)"
source: "ICM_map.md"
tags: [agentic, agents, context-engineering, icm, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

### Mindmap Plan: Interpretable Context Methodology (ICM)

**Central Topic:** **Interpretable Context Methodology (ICM)**
- **Tagline:** Folder Structure as Agent Architecture

---

#### 1. The Problem & Core Idea
- **Problem with Current Frameworks:** (LangChain, AutoGen, CrewAI)
    - High engineering overhead for sequential workflows.
    - Changes require code edits and redeployment.
    - Opacity: Hard to inspect intermediate state.
- **The Core Idea:** For sequential, human-reviewed tasks, the filesystem *is* the orchestrator.
    - One agent reads the right files at the right time.
    - Folder structure dictates role, context, and sequence.
- **The Central Question:** How does filesystem-based context delivery affect control, inspectability, and output quality?

---

#### 2. Foundational Principles & Lineage
- **Design Principles (The "Five Rules")**
    1.  [One Stage, One Job.md](One Stage, One Job.md) : Single responsibility per folder.
    2.  [Plain Text as Interface.md](Plain Text as Interface.md) : Markdown/JSON as the universal communication layer.
    3.  **Layered Context Loading:** Load only what's needed for the current stage.
    4.  **Every Output is an Edit Surface:** Human-in-the-loop at every step.
    5.  **Configure the Factory, Not the Product:** Separate stable config from per-run output.
- **Intellectual Lineage**
    - **Software Engineering:**
        - **Unix Philosophy:** (McIlroy, Kernighan & Pike) "Do one thing well," text streams.
        - **Make & Build Systems:** (Feldman) Files as artifacts and coordination.
        - **Pipe-and-Filter Pattern:** (Shaw & Garlan) Reusable, inspectable components.
        - **Multi-Pass Compilers:** Intermediate representations between stages.
        - **Literate Programming:** (Knuth) Documentation and code as one.
    - **Context Engineering:**
        - **Beyond "Prompting":** (Karpathy) Context as the core system to design.
        - **"Lost in the Middle":** (Liu et al.) Justifies scoping context to avoid degradation.
        - **Not MCP:** Complementary to Anthropic's Model Context Protocol (scoping vs. access).
    - **Human Oversight:**
        - **Mixed-Initiative Systems:** (Horvitz) Natural breakpoints for human control.
        - **Appropriate Trust:** (Lee & See) Trust requires observable behavior.
        - **Inherent Interpretability:** (Rudin) Build transparent systems, don't explain opaque ones.

---
