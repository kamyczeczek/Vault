---
type: Concept
id: 03_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 4/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

These hybrid formulations highlight a broader paradigm: using LLMs as flexible natural-language
interfaces while delegating correctness and reliability to symbolic or algorithmic components.
LLMs and Planning. In challenging tasks, an agent may need to generate a plan before completing
the task. Many researchers have investigated how LLMs can be used effectively for planning (26) (25)
(14). There have been impressive gains in this area of research; for example, a recent notable example
is by Verma et al. (30) which claims up to 94% planning accuracy using a fine-tuning approach paired
with chain-of-thought reasoning. Despite these gains, planning remains a challenging task ( 24) (29)
with many results showing that LLMs still have many weaknesses when applied to these problems.
Furthermore, many approaches still require considerable scaffolding.
A consistent claim is that the effectiveness of LLM planning is reduced as task complexity increases.
Kambhampati (13) argues that LLMs engage in universal approximate retrieval, where they rely on
pattern matching rather than systematic reasoning. This suffices for generating immediate solutions or
short inference chains, but can run into issues when task complexity increases, which can be seen in
ACPBench (16) where the task of generating just the next action has a much higher success rate than
the more complex tasks. This suggests that current LLMs are most effective at solving short tasks that
do not need multi-step planning. A natural solution would be as follows: When the provided task is too
complex for an LLM agent, decompose the task into subtasks for which the LLM is effective.
Unlike other works in this area, our focus is not directly on the ability of an LLM to produce a plan
(i.e., a sequence of steps solving the planning task). Rather, in many tasks that agentic LLMs are
applied to solve, a sort of meta-planning is a requisite process for solving complex problem instances.
By decomposing a task into smaller subtasks, the meta-planning required will be less complex and the
agentic system will be less impacted by weaknesses of current LLMs when encountering complex tasks.
3 Preliminaries
We represent procedural knowledge using a Hierarchical Task Network (HTN), described next. We then
formalize the problem as a Markov Decision Process (MDP) where the policy that solves the MDP is an
LLM. Finally, we analyze why we expect ProcLLM to perform well.
Hierarchical Task Networks (HTNs). Because our focus is on how procedural knowledge improves
LLM performance, our description of HTNs sacrifices exact formality for a more notional understanding.
A full formal treatment can be found in ( 8). Let K be a set of tasks; a task κ∈K is a labeled name
of something the system needs to do. Figure 1 (top) shows an HTN decomposition tree where K
relates to the travel problem from §1. HTNs decompose complex tasks (white boxes) into primitive
tasks (gray boxes) using methods (ovals).Complex tasksdescribe abstract tasks that need to be
decomposed andprimitive tasksdescribe concrete executable tasks. Figure 1 shows two methods.
Method m-process-user-request decomposes κp into ⟨κ1, .., κ4⟩, where the κ1 (dashed box) has passed
the verify check (described below). Method choose departing flight decomposes κ2 into primitive
tasks:⟨understand flight tool,write flight to notes⟩.
For a set of methods M, a method m∈ Mis a tuple (head, task, pre, subtasks), where the head is the
name and any paramaters of the method, task matches the taskname the method can decompose, pre
is a (possibly empty) set of preconditions for applying the method in a state, and subtasks is a totally
ordered sequence of tasks ⟨κ1, κ2, .., κn⟩. A method that matches a task isrelevant, and HTN planners
often select the first relevant method in M (As described in §4, ProcLLM’s Algorithm 1, Line 24 uses
FindFirstRelevantMethod to select methods).
Markov Decision Process (MDP) Model. We formalize agentic tasks as a finite-horizon deterministic
Markov Decision Process (MDP), defined by the tuple M= (S,A,T, r, H), where S is the set of states
with a subset of absorbing terminal states, Sterm ⊂ S, A is set of actions, T:S × A → Sis a deterministic
state transition function, where si+1 =T(s i, ai), r:S × A →Ris a reward function, and H is a finite
horizon. An episode terminates either by reaching a terminal state or by exceeding the horizon (timeout).
4
