---
type: Concept
id: 01_icm_map
title: "ICM_map.md (part 2/3)"
source: "ICM_map.md"
tags: [agentic, agents, context-engineering, icm, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
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
