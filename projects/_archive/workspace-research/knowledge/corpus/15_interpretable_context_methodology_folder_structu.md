---
type: Concept
id: 15_interpretable_context_methodology_folder_structu
title: "Interpretable Context Methodology: Folder Structure as Agent (part 16/21)"
source: "Interpretable Context Methodology Folder Structure as Agent.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, interpretable-context]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

16•Jake Van Clief, David McDermott
model’s output quality and the human’s ability to steer, inspect, and correct that output. ICM provides a concrete
platform for investigating these questions because its architecture makes the context structure explicit, editable,
and observable at every stage.
6 Future Directions: Compilation, Debugging, and Source Integrity
The previous sections describe ICM as it currently works in production. This section describes where it should
go next. The ideas here are informed by early practitioner experience and by a structural analogy that the paper
has not yet drawn: the relationship between ICM workspaces and multi-pass compilers.
6.1 ICM as Multi-Pass Incremental Compilation
The paper has grounded ICM in Unix pipelines, Make, and the pipe-and-filter pattern. There is a closer analogy
that deserves attention: multi-pass compilation [52].
A multi-pass compiler transforms source code through a sequence of discrete passes. The lexer produces tokens.
The parser produces a syntax tree. Semantic analysis annotates the tree. Optimization passes rewrite it. Code
generation produces the final output. Each pass reads the output of the previous pass, transforms it according
to its own rules, and writes an intermediate representation that the next pass can consume. The intermediate
representations are well-defined, inspectable, and (in debugging builds) preserved for examination.
ICM does the same thing with content. Stage 1 (research) transforms a topic brief into structured research
output. Stage 2 (script) transforms the research output into a script. Stage 3 (production) transforms the script
into animation specifications and code. Each stage reads the previous stage’s output, applies its own context and
instructions, and writes an intermediate artifact that the next stage consumes. The intermediate artifacts are
plain files that can be opened, read, and edited.
The analogy extends further. Incremental compilation means recompiling only the parts of the program
that changed, rather than rebuilding from scratch. ICM supports this by default: if the research output is fine
but the script needs rework, the practitioner re-runs stage 2 without touching stage 1. If a voice guide in the
reference material changes, only the stages that load that file need to run again. The folder structure tracks these
dependencies implicitly: a stage’s Inputs table declares which files it reads, and a change to any of those files
signals that the stage’s output may be stale.
This is worth naming because it connects ICM to a body of compiler engineering that has spent fifty years
solving the problems of pass decomposition, intermediate representation design, and selective recompilation.
The current paper draws from Unix and software architecture. Future work should draw from compiler theory as
well, particularly around dependency tracking, change propagation, and the formal properties of intermediate
representations.
6.2 Toward Semantic Debugging
Traditional debugging rests on a simple principle: when the output is wrong, trace the failure back through the
program’s execution to find the instruction that caused it [53]. Debuggers provide tools for this: breakpoints that
pause execution at specific instructions, stack traces that show the call chain, variable inspection that shows
state at each point, and source maps that connect compiled output back to the original source.
ICM currently provides observability but not traceability. A practitioner can open any stage’s output folder
and read what the agent produced. But if a phrase in the stage 3 output sounds wrong, there is no direct way
to trace that phrase back to the specific instruction, reference file, or previous stage output that caused it. The
practitioner has to do this manually: read the stage 3 contract, check which files it loaded, read those files, and
form a judgment about which source is responsible. This works. It is how most ICM debugging happens today.
But it is the equivalent of debugging a program by reading the source code and thinking hard, without a debugger.
