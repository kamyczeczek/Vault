---
type: Concept
title: ICM_map
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

#### 3. The ICM Architecture
- **The Five-Layer Context Hierarchy**
    - **Layer 0: Global Identity:** (`CLAUDE.md`) "Where am I?" (~800 tokens).
    - **Layer 1: Task Routing:** (`CONTEXT.md`) "Where do I go?" (~300 tokens).
    - **Layer 2: Stage Contract:** (`stages/XX/CONTEXT.md`) "What do I do?" (200-500 tokens). The core control point.
    - **Layer 3: Reference Material:** (`references/`, `_config/`) "The Factory." Stable rules, style guides. (500-2k tokens).
    - **Layer 4: Working Artifacts:** (`output/`) "The Product." Per-run inputs/outputs. (Variable).
- **Key Distinction:** **Layer 3 (Reference) vs. Layer 4 (Working)**
    - **Layer 3:** Stable, internalize as constraints. (e.g., `voice.md`).
    - **Layer 4:** Dynamic, process as input. (e.g., `research-output.md`).
    - This separation cleans the model's context and improves performance.
- **Stage Contracts (`stages/XX/CONTEXT.md`)**
    - **Inputs Table:** Explicitly lists which Layer 3 and Layer 4 files to load.
    - **Process:** Instructions for the transformation.
    - **Outputs:** Where to write the result (`output/`).
- **Visual Structure & Flow:**
    - Folder numbering encodes sequence (01, 02, 03...).
    - Stage output folders are the handoff points for the next stage or a human reviewer.
    - Creates "Review Gates" for human-in-the-loop editing.

---

#### 4. Evidence & Implementation
- **Workspaces Tested:**
    - Script-to-Animation Pipeline (3 stages).
    - Course Deck Production (5 stages).
    - ICM Workspace-Builder (A workspace that builds workspaces).
- **Early Practitioner Findings:**
    - **U-Shaped Intervention:** Heavy human edits at Stage 1 (direction) and final stage (alignment/debugging). Light edits in the middle.
    - **Accessibility:** Non-developers successfully edit prompts and run pipelines by editing markdown files.
    - **Portability:** Workspaces are duplicated and adapted by copying folders.
- **Threats to Validity:** (Self-reported data, single model family, no formal controlled study).

---

#### 5. Discussion: Scope & Implications
- **Where ICM Works:**
    - Sequential, reviewable, repeatable workflows.
    - Content production, research analysis, policy workflows.
- **Where ICM Does NOT Work:**
    - Real-time multi-agent collaboration (needs message-passing).
    - High-concurrency systems (needs queueing, state isolation).
    - Complex automated branching logic (requires code).
- **Key Implications:**
    - **Observability as a Side Effect:** "Glass-box" workflows due to plain-text artifacts.
    - **Context Scoping:** Architectural prevention of "lost in the middle" vs. post-hoc compression.
    - **Regulatory Alignment:** Natural fit for EU AI Act requirements (human oversight, audit trails).

---

#### 6. Future Directions: The Compiler Analogy
- **ICM as Multi-Pass Compilation:**
    - Stages as compiler passes; outputs as Intermediate Representations.
    - Supports **incremental compilation** (re-run only changed stages).
- **Toward Semantic Debugging:**
    - **Problem:** Currently observability without traceability. Can't directly trace an error in Stage 3 output back to its source in Stage 1.
    - **Proposed Tools:**
        - **Output Provenance:** Link output sections to source instructions/reference files (like source maps).
        - **Cross-Stage Trace Verification:** Add "Verify" sections to stage contracts to check alignment between stages.
        - **Breakpoints in Markdown:** Pause within a stage for inspection.
- **Source Integrity & the Edit-Source Principle:**
    - **Argument:** Editing output is "patching the binary." Editing the source (`CONTEXT.md`, `voice.md`) "fixes the compiler."
    - **Goal:** Track output edits to suggest source-level improvements, making workspaces that improve over time.

---

#### 7. Conclusion
- **Summary:** ICM applies 50-year-old Unix principles to modern AI orchestration.
- **The Value Proposition:** Simplest viable architecture for a common class of problems.
- **The Artifact:** The workspace is a portable, editable, inspectable folder. Open-source and accessible.
