---
type: Concept
id: 09_interpretable_context_methodology_folder_structu
title: "Interpretable Context Methodology: Folder Structure as Agent (part 10/21)"
source: "Interpretable Context Methodology Folder Structure as Agent.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, interpretable-context]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

10•Jake Van Clief, David McDermott
Wei et al. demonstrated that breaking complex reasoning into intermediate steps dramatically improves LLM
performance [27]. ICM applies this finding architecturally: complex workflows are decomposed into stages with
explicit boundaries, and each stage receives focused, stage-appropriate context. The model gets a clear, scoped
task at each step rather than a monolithic instruction to do everything in a single pass.
3.4 Portability and Reproducibility
A workspace is a folder. It can be copied to another machine, committed to Git, emailed as a zip file, or synced
through any cloud storage service. It carries its own prompts, its own context structure, its own stage definitions.
There is no server to configure, no environment to replicate, no deployment step.
ICM workspaces are Git-compatible by default [13]. Every change to a prompt, every edit to a stage output,
every configuration adjustment is diffable and reversible. Stage outputs can be committed after each run, creating
a version history of the entire production pipeline’s behavior over time. This is infrastructure as code [14] applied
to AI workflows: the workspace definition is the system. There is no separate deployment artifact.
This portability matters for a practical reason. If a consultant builds a workspace for a client’s weekly reporting
workflow, handing it over means copying a folder. The client can run it, edit the prompts to match their evolving
needs, and adjust stages without involving a developer. The same handoff with a framework-based solution
typically requires documentation, environment setup, dependency management, and ongoing technical support.
4 Working Implementations
ICM is not a theoretical proposal. The protocol has been implemented and tested across several production
workflows.5
4.1 Model and Environment
All workspaces described here were developed and run using Claude Code with Claude Opus 4.6 as the primary
agent [54]. For sub-agent tasks within stages, Opus 4.6 delegates to Claude Sonnet 4.6 through its Agent Teams
capability, which coordinates multiple agents working in parallel from a single orchestrator.
A detail worth noting: Opus 4.6 uses the workspace’s own context files, the CONTEXT.md hierarchy and Layer 3
reference material, to fill prompts for its sub-agents. The model reads the folder structure to determine what
context each sub-agent should receive and what task it should perform. This means the ICM architecture is doing
double duty. It structures context for the primary agent, and it provides the specification that the primary agent
uses to delegate work. The folder hierarchy is both the human’s control surface and the model’s orchestration
logic.
ICM is designed to be model-agnostic. The protocol specifies folder structure, file formats, and naming
conventions. It does not depend on any model-specific capability. A workspace built for Claude could be run
with a different model by pointing that model at the same files. Whether the results would be equivalent is an
empirical question that depends on how different models handle the same context, but the protocol itself imposes
no vendor lock-in. The workspaces described below were tested with the models listed above.
4.2 Script-to-Animation Pipeline
The first workspace built on ICM takes a content idea through three stages to produce a working animated video.
Stage 1 (01_research) takes a topic and produces structured research output: key points, narrative angles,
supporting data. The agent reads a research brief from the user and writes a research document to its output
folder.
5All workspaces referenced here are available or buildable through the ICM repository at https://github.com/RinDig/Interpretable-Context-
Methodology-ICM-.
