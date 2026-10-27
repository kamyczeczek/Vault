---
type: Concept
id: 00_adapt_as_needed_decomposition_and_planning_with
title: "ADAPT: As-Needed Decomposition and Planning with Language Models (part 1/28)"
source: "ADAPT As-Needed Decomposition and Planning with Language Models.pdf"
tags: [LLM, Products, Think, agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

ADAPT: As-Needed Decomposition and Planning with Language Models
Archiki Prasad♣ Alexander Koller♡ Mareike Hartmann♡
Peter Clark♠ Ashish Sabharwal♠ Mohit Bansal♣ Tushar Khot♠
♣ UNC Chapel Hill ♠ Allen Institute for AI ♡ Saarland University
Abstract
Large Language Models (LLMs) are increas-
ingly being used for interactive decision-
making tasks requiring planning and adapt-
ing to the environment. Recent works em-
ploy LLMs-as-agents in broadly two ways:
iteratively determining the next action (itera-
tive executors) or generating plans and execut-
ing sub-tasks using LLMs (plan-and-execute).
However, these methods struggle with task
complexity, as the inability to execute any
sub-task may lead to task failure. To ad-
dress these shortcomings, we introduce As-
Needed Decomposition and Planning for com-
plex Tasks (ADAPT), an approach that explic-
itly plans and decomposes complex sub-tasks
as-needed, i.e., when the LLM is unable to ex-
ecute them. ADAPT recursively decomposes
sub-tasks to adapt to both task complexity and
LLM capability. Our results demonstrate that
ADAPT substantially outperforms established
strong baselines, achieving success rates up to
28.3% higher in ALFWorld, 27% in WebShop,
and 33% in TextCraft – a novel compositional
dataset that we introduce. Through extensive
analysis, we illustrate the importance of multi-
level decomposition and establish that ADAPT
dynamically adjusts to the capabilities of the
executor LLM as well as to task complexity.1
1 Introduction
Recent advances in Large Language Models
(LLMs) have expanded their application beyond
conventional NLP tasks to more complex tasks
involving mathematical, symbolic, and common-
sense reasoning (Wei et al., 2022; Huang and
Chang, 2023). Recent models have even been ap-
plied to decision-making tasks, such as performing
household chores, navigating a webpage, etc., that
require interactions with external environments or
tools (Yao et al., 2023b; Qin et al., 2023).
1Project: https://allenai.github.io/adaptllm
Prior works on using LLMs for decision-making,
such as ReAct (Yao et al., 2023b), iteratively gen-
erate the next action to be executed in the environ-
ment given the history of actions and observations
(see Fig. 1; top-left). However, as the tasks become
more complex, LLMs struggle due to their limited
composition ability (Dziri et al., 2023) and inability
to deal with the distractors (Shi et al., 2023) in a
long action-observation trajectory.
To mitigate this, modular approaches (Khot et al.,
2023; Yang et al., 2023; Sun et al., 2023) incorpo-
rate a separate planner module that utilizes an LLM
to create a high-level plan.2 The planner then dele-
gates simpler sub-tasks to an executor LLM module
thereby reducing the compositional complexity and
length of action trajectory required by the execu-
tor. We refer to this category broadly as plan-and-
execute approaches (see Fig. 1; top-right). While
the plans enable these methods to guide the execu-
tion and track progress (Wang et al., 2023b), their
non-adaptive nature poses a limitation when con-
fronting unachievable sub-tasks. These approaches
inherently lack the flexibility to adapt to task com-
plexity and manage execution failures, as shown
in Fig. 1(top-right), where just one sub-task that is
too complex results in overall task failure.
To address such failures, we proposeAs-Needed
Decomposition and Planning for complex Tasks
(ADAPT), a recursive algorithm that further de-
composes sub-tasks when necessary, to dynami-
cally accommodate to task complexity. We uti-
lize separate planner and executor LLM modules
within our framework but only decompose a task
using the planner, if the executor LLM detects a
failure. As shown in Fig. 1, the overall task of
putting a clean mug on a desk in an unfamiliar
2By “planning”, we refer to the colloquial concept of
designing a list of sub-tasks to accomplish a complex task
rather than its usage in classical AI-planning literature. E.g.,
a “plan” for preparing a lasagna could be to cook the pasta,
prepare the sauce, layer the ingredients, and then bake it.
arXiv:2311.05772v2  [cs.AI]  8 Apr 2024
