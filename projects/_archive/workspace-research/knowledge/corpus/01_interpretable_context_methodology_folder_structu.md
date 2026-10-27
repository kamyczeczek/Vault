---
type: Concept
id: 01_interpretable_context_methodology_folder_structu
title: "Interpretable Context Methodology: Folder Structure as Agent (part 2/21)"
source: "Interpretable Context Methodology Folder Structure as Agent.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, interpretable-context]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

2•Jake Van Clief, David McDermott
Table 1. Comparison of control surfaces for sequential, human-reviewed workflows. The first six rows show dimensions
where ICM’s filesystem approach simplifies common operations. The last four rows show dimensions where framework-based
approaches provide capabilities that ICM lacks or handles less well.
Dimension Framework approach ICM approach
Change stage order Edit orchestration code, rede-
ploy
Rename or reorder folders
Modify a prompt Edit agent configuration in code Edit a markdown file
Add or remove a stage Write new agent class, update
orchestrator
Add or delete a folder
Inspect intermediate
state
Add logging, build dashboard Open the folder, read the files
Hand off to another
person
Document environment, depen-
dencies, setup
Copy the folder
Who can make
changes
Developer Anyone with a text editor
Error recovery mid-
pipeline
Built-in retry, fallback, excep-
tion handling
Manual re-run of failed stage
Conditional branching Programmatic routing based on
agent output
Human decides between stages
Concurrent execution Native parallel agent coordina-
tion
Sequential by design
External service inte-
gration
Programmatic API calls, auth
management
Local scripts or MCP connec-
tions
The paper is organized as follows. Section 2 traces the relevant background across software engineering,
context engineering, and human oversight research. Section 3 describes the protocol itself. Section 4 walks
through working implementations and reports on early practitioner experience. Section 5 discusses where this
approach fits and where it does not, including implications for the design of interactive intelligent systems more
broadly. Section 6 explores future directions, drawing on the structural parallels between ICM and multi-pass
compilation to propose semantic debugging and source-level traceability for AI workflows.
2 Background and Related Work
2.1 Composability and the Unix Tradition
In 1978, Doug McIlroy articulated the principles that would define Unix’s design philosophy: make each program
do one thing well, expect the output of every program to become the input to another, and use text streams as the
universal interface between programs [1]. These principles were not theoretical. They were engineering decisions
driven by constraints. The PDP-11 machines that ran early Unix had limited memory. Programs had to be small.
The way to build powerful systems from small programs was to connect them through a common interface [2].
