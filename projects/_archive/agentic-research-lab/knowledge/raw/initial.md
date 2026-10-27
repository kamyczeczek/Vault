---
type: Concept
title: initial
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

Here is a curated list of scientific sources on creating agentic research processes, organized by the type of contribution they make to the field.

### 📚 Surveys & Conceptual Frameworks
These papers provide taxonomies, design blueprints, and conceptual overviews for building scientific agents.

| Source                                                       | Key Contribution                                             | Venue/Year                 |
| ------------------------------------------------------------ | ------------------------------------------------------------ | -------------------------- |
| **The Hitchhiker's Guide to Autonomous Research: A Survey of Scientific Agents** | Proposes a unified taxonomy based on **capability envelope and maturity**, and clarifies how scientific agents differ from general-purpose agents in goal orientation, workflow embedding, and scientific commitments. | IEEE TPAMI, 2026           |
| **From Automation to Autonomy: A Survey on Large Language Models in Scientific Discovery** | Introduces a foundational **three-level taxonomy—Tool, Analyst, and Scientist**—to delineate escalating autonomy and evolving responsibilities within the research lifecycle. | EMNLP 2025                 |
| **Toward autonomous science with agentic artificial intelligence** | Traces the emergence of agentic scientific reasoning, discusses scaling laws and autonomous laboratories, and highlights challenges in hallucination, bias, and reproducibility. | Cell (ScienceDirect), 2026 |

### 🔬 End-to-End Research Systems
These are full-fledged frameworks that attempt to automate the entire research pipeline, from hypothesis generation to manuscript writing.

| Source                                                       | Key Contribution                                             | Venue/Year                     |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------ |
| **Closing the Empirical Loop: Autonomous AI Agents Conduct End-to-end Research With Human Participants** | Demonstrates a domain-agnostic agentic AI Scientist that **autonomously designed and executed three psychological studies** with 288 human participants, including hypothesis generation, data collection, and manuscript preparation. | Advanced Science (Wiley), 2026 |
| **Agent Laboratory: Using LLM Agents as Research Assistants** | An autonomous LLM-based framework that progresses through **literature review, experimentation, and report writing**, producing a code repository and research report. Achieved an 84% cost reduction compared to previous methods. | Findings of EMNLP 2025         |
| **Autonomous Research Loops: An LLM-Agent Framework for End-to-End ML Experimentation, Manuscripting, and Self-Evaluation** | Employs LLM-based agents to automate the **entire life cycle of ML research**, including a conference-specification-aware reviewer agent for self-evaluation. Generates medium-quality artifacts at ~$15 per paper. | IECA 2026 (ACM)                |
| **Towards end-to-end automation of AI research**             | Details a system that iterates through **idea generation, experiment execution, and manuscript generation**, using Aider to modify codebases and automatically debug runtime errors. | Nature, 2026                   |

### 🤝 Multi-Agent Architectures
These sources focus on collaborative multi-agent systems that emulate the division of labor in human research teams.

| Source                                                       | Key Contribution                                             | Venue/Year                                                   |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Beyond static responses: multi-agent LLM systems as a new paradigm for social science research** | Discusses systems like **Sakana AI's AI Scientist** and **Google's AI Co-Scientist**, which orchestrate heterogeneous agents (hypothesis generators, experimental designers, result analysts) across iterative research loops, incorporating principles of diversity and redundancy. | Humanities and Social Sciences Communications (Nature), 2026 |
| **AgenticSciML: collaborative multi-agent systems for emergent discovery in scientific machine learning** | Describes a system with specialized agents for **exploratory data analysis, evaluation contract generation, and root solution generation**, using ensemble-guided parent selection for evolutionary search. | npj Artificial Intelligence (Nature), 2026                   |
| **AutoLabs: cognitive multi-agent systems with self-correction for autonomous chemical experimentation** | A multi-agent system with **self-correction** capabilities applied to autonomous chemical experimentation. | Scientific Reports (Nature), 2026                            |

### 🧑‍🔬 Human-AI Collaboration & Practical Guides
These sources emphasize frameworks where humans remain in the loop, providing methodological rules and practical guidance.

| Source                                                       | Key Contribution                                             | Venue/Year                         |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ---------------------------------- |
| **The Agentic Researcher: A Practical Guide to AI-Assisted Research in Mathematics and Machine Learning** | Provides a **five-level taxonomy of AI integration** and an open-source framework that turns CLI coding agents (e.g., Claude Code, Codex CLI) into autonomous research assistants via agent prompts. Longest autonomous session ran for over **20 hours**. | arXiv, 2026                        |
| **TinyScientist: An Interactive, Extensible, and Controllable Framework for Building Research Agents** | Identifies essential components of the automatic research workflow and proposes an **interactive, extensible, and controllable framework** that adapts to new tools and supports iterative growth. | EMNLP 2025 (System Demonstrations) |
| **Building MCP-native hierarchical AI scientist ecosystems** | Argues for **Model Context Protocol (MCP)-native agents** organized through hierarchies inspired by human society, proposing pathways to increase scaling capabilities via composability and autonomous invention of new agents and workflows. | OSTI/Frontiers in AI, 2026         |

### ⚠️ Key Considerations & Limitations
Across these sources, several recurring themes and challenges emerge:

- **Human oversight remains critical.** Even the most autonomous systems benefit from human feedback at key stages; Agent Laboratory found that incorporating human involvement improves overall research quality .
- **Failure modes are documented.** Common issues include **hallucination of experimental details, broken implementations, and misinterpretation of metrics** . The "Closing the Empirical Loop" paper notes limitations in **conceptual nuance and theoretical interpretation** compared to experienced researchers .
- **Verification mechanisms are essential.** Frameworks stress the need for **effective verification mechanisms and safety constraints** incorporated from the outset to ensure reproducible and auditable AI-powered scientific progress .
- **Cost and efficiency are improving.** Systems like Agent Laboratory report an **84% decrease in research expenses** compared to previous autonomous methods, while generating state-of-the-art machine learning code .

If you would like me to dive deeper into any specific framework or retrieve the full text of a particular paper, just let me know.