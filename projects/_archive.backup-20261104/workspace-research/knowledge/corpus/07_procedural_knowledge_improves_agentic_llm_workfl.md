---
type: Concept
id: 07_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 8/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

see Appendix B.2). The environment implements a transition function as a set of scripts that calls
Exec(Solver)and otherwise modifies files as indicated in the actions.
Tasks K and Methods M. For ProcLLM, the tasks and methods are domain-dependent. Most domains
will have the taskprocess user request, which is the top level task that the agent will start with. Figure 1
shows some simplified methods and their associated sub/tasks; the actual methods and tasks in the
system’s code differs slightly from this simple form. For the methods in this system, no preconditions
are specified. In addition to the (head, task, subtask), methods in ProcLLM also include details for the
verifystep.
As an example, in Figure 1, the most abstract task process user request decomposes into four subtasks
(Lines 3-6) and the verify context includes additional details (Lines 7-9). The second subtask choose
departing flight is further decomposed by m-choose-departing-flight (Lines 10-17) where one of the
subtasks is to understand the flight tool, as described inm-understand-flight-tool(Lines 18-22).
Workflow of ProcLLM. Figure 2 shows an overview of the system with the key components of the
system. Along the top of the diagram, moving left to right, are the agentic components that produce an
action. The bottom of the diagram shows the components that make up the environment.
Algorithm 1 provides pseudocode for ProcLLM. If methods M are provided, Line 2 calls UpdateTask
to decompose K. UpdateTask (Lines 23-27) decomposes head(K) if there are relevant methods. If
verified is True, UpdateTask will remove head(K) and may further decompose K, where the leaves are
primitive tasks that describewhataction-LLM should do. K remains unchanged if verified is False, M
is empty, or there are no relevant methods forhead(K).
After calling UpdateTask, ProcLLM then processes a sequence of tasks K up to the horizon H (Line 3)
or until K is empty (Line 4). Line 6 assembles an action context Ca from the current environment
state s, the execution trace of the last system execution, and the current task κ. Ca is processed by
action-LLM (Line 7) which produces a parameterized action a, which is either an internal verify action
or an external read/write/append action. For averify action (Lines 9-15), Line 10 assembles a verify
contextC v from the system state and current task, which is processed by the verify-LLM (Line 11).
If there remain tasks to complete, Lines 16-22 execute external actions in the environment. These
external actions are JSON output that is parsed into an action a. For this paper, a set of python scripts
implements the transition T(s ,a)), which produces a new system state a that is fed into the agent for the
next cycle.
5 Empirical Evaluation
We evaluate ProcLLM on two benchmarks with external APIs and two with a combinatorial solution
space often solved with search, summarized in the table below.Travel Planning (TP), based on
(33), requires booking a single-city itinerary using several tools.Recipe Generator (RG), a synthetic
problem, requires proposing a recipe from a list of ingredients using a tool and solver.Blocks World
(BW), a planning benchmark ( 28), requires rearranging stacks of blocks.Unit Movement (UM),
another synthetic benchmark, requires moving units around a graph.
Solver? Tools ? Problem Type Source
TP Y Y Tool Use (33)
RG Y Y Algorithmic Tool Use This paper
BW Planning (28)
UM Game This paper
The agent is given a horizon of H= 100 . Solutions are automatically verified using human-written
simulators and test functions. We test three conditions: human-created M (Human-TN), LLM-created
M (LLM-TN), or M=∅ (No-TN). ForNo-TN, K has one task describing the end conditions for solving the
9
