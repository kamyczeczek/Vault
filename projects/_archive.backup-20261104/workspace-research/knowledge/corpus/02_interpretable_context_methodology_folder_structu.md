---
type: Concept
id: 02_interpretable_context_methodology_folder_structu
title: "Interpretable Context Methodology: Folder Structure as Agent (part 3/21)"
source: "Interpretable Context Methodology Folder Structure as Agent.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, interpretable-context]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Interpretable Context Methodology: Folder Structure as Agent Architecture•3
Kernighan and Pike later argued that the power of a Unix system comes more from the relationships among
programs than from the programs themselves [5]. Eric Raymond codified this into explicit design rules: the Rule
of Modularity (write simple parts connected by clean interfaces), the Rule of Transparency (design for visibility
to make inspection and debugging easier), and the Rule of Composition (design programs to be connected to
other programs) [4].
These principles were formalized in software architecture as the “pipe-and-filter” pattern by Shaw and Garlan
[6]: a system of independent components, each reading from inputs and writing to outputs, connected by data
streams. The pattern’s strength is that any component can be replaced, inspected, or tested independently.
A related lineage runs through build systems. Stuart Feldman’s Make (1979) established that workflows could
be defined as dependency graphs between files using declarative specifications [7]. The key insight: files are both
the artifacts of work and the coordination mechanism between stages. You do not need a separate orchestration
layer when the filesystem tracks what has been produced and what depends on it. Multi-pass compilers work
on the same principle: source code transforms through a sequence of intermediate representations, each pass
reading the output of the previous pass, with well-defined interfaces between them [52].
David Parnas argued in 1972 that systems should be decomposed based on what each module hides from
the rest of the system, yielding components that can be modified independently [9]. Edsger Dijkstra coined the
term “separation of concerns” to describe the discipline of addressing one thing at a time as the only available
technique for effective ordering of one’s thoughts [8].
These ideas appear across decades and contexts because they describe something real about how systems stay
manageable as they grow. They are relevant here because the problem of orchestrating AI agents through multi-
step workflows is, at its core, a problem of modular decomposition, clean interfaces, and readable intermediate
representations.
2.2 Context Engineering and Agentic AI
The practitioner community has increasingly adopted the term “context engineering” to describe what building
production AI systems actually involves. Andrej Karpathy gave the term its clearest articulation in June 2025,
arguing that “prompt engineering” understates the work [ 16]. The distinction is useful. Prompt engineering
suggests crafting a single instruction. Context engineering describes the broader discipline of filling the context
window with the right information: instructions, retrieved knowledge, memory, tool descriptions, and prior
outputs, all structured so the model can use them effectively. This paper uses the term in that sense.
Lance Martin at LangChain formalized this into a taxonomy of strategies: write (author instructions), select
(choose relevant context), compress (reduce token waste), and isolate (keep unrelated context separate) [ 17].
Simon Willison argued that the entire information environment, including previous model responses and system
state, is part of the context that needs engineering [18].
The current generation of agentic frameworks, LangChain [21], AutoGen [20], CrewAI, and others, handle
context engineering through code-level abstractions. They define agents as objects, conversations as message
arrays, and orchestration as programmatic control flow. This works well for systems that need dynamic multi-
agent collaboration, concurrent execution, or complex branching logic.
But for sequential workflows, these frameworks solve a coordination problem that may not need to exist. If
Agent A’s job is to research, Agent B’s job is to filter, and Agent C’s job is to write, the framework’s role is to
pass the right context to the right agent at the right time. That coordination can also be achieved by putting the
right files in the right folders. The orchestrating agent reads different instructions at each stage. If it delegates
sub-tasks to smaller models (as current agent-team architectures allow), the folder structure provides the context
for those delegations too. The coordination logic lives in the filesystem, not in application code.
