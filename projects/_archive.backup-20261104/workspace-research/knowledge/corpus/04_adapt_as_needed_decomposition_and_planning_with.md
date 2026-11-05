---
type: Concept
id: 04_adapt_as_needed_decomposition_and_planning_with
title: "ADAPT: As-Needed Decomposition and Planning with Language Models (part 5/28)"
source: "ADAPT As-Needed Decomposition and Planning with Language Models.pdf"
tags: [LLM, Products, Think, agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

if the executor does not succeed, the controller dele-
gates decomposing the complex task to the planner
and recursively calls ADAPT for each sub-task un-
til we hit a termination criterion, i.e., if a maximum
depth dmax (≥1) is reached.
Fig. 2 (mid) shows the control flow of ADAPT.
A complex task such as “put a clean mug on the
desk” is first assigned to the executor. If the execu-
tor does not succeed, thenADAPT calls the planner
to decompose the task into sub-tasks along with a
logical operator ( AND or OR) indicating how to
compose them. Each sub-task (referred to as ‘step’
in Fig. 2) is then assigned recursively to ADAPT
and is combined using the logical operator. In the
end, the success of sub-tasks after recursive decom-
position ensures overall task success (unrolled calls
to planner and executor are shown in Fig. 1).
4 Experimental Setup
We describe the datasets used in our experiments
and baselines used for comparison with ADAPT.
4.1 Datasets
We employ LLMs-as-agents to perform tasks in the
following three environments and use task success
rate as our evaluation metric in Secs. 5 and 6.
ALFWorld. ALFWorld (Shridhar et al., 2021)
is a text-based game version of the embodied AL-
FRED benchmark (Shridhar et al., 2020) imple-
mented in the TextWorld environment (Côté et al.,
2019). It encompasses 6 distinct task types, where
an agent is required to accomplish high-level tasks
through navigation and interaction via text-based
actions in a simulated household that gives textual
feedback to an agent (e.g., put a clean mug on desk
discussed earlier in Fig. 2). Following Shridhar
et al. (2021), we present results on 134 unseen eval-
uation games (test set) with a separate dev set of
10 games per task from the seen evaluation games
split. Along with atomic skills, we add example
gold trajectories, following Yao et al. (2023b), for
two tasks: heat and look in the executor prompt.3
WebShop. WebShop (Yao et al., 2022) is an on-
line shopping website environment featuring 1.18
million real-world products containing 500 user
queries in the test set. It serves as a complex
3Unlike Yao et al. (2023b), we use a standardized executor
prompt for all ALFWorld tasks, avoiding the agent to know the
task-type apriori. Table 6 in Appendix C further demonstrates
that ADAPT still improves over task-specific executors.
Crafting Commands:
craft 4 oak planks using 1 oak log
craft 1 honeycomb block using 4 honeycomb
craft 1 beehive using 6 planks, 3 honeycomb
Goal: craft beehive
[Action] get 1 oak log
[Env] Got 1 oak log
[Action] craft 4 oak planks using 1 oak log
[Env] Crafted 4 minecraft:dark_oak_planks
[Action] get 1 oak log
[Env] Got 1 oak log
[Action] craft 4 oak planks using 1 oak log
[Env] Crafted 4 minecraft:dark_oak_planks
[Action] craft 1 beehive using 6 oak planks, 3 honeycomb
[Env] Crafted 1 minecraft:beehive
...
1x1x
4x 4x 3x
1x
Figure 3: Example gold trajectory in TextCraft for a
task with recipe depth of 2.
decision-making environment with practical appli-
cations wherein an agent must navigate a website
through a variety of commands to purchase an item
matching a user specification (e.g., grey sectional
sofa priced less than $300 with fast delivery). Fol-
lowing Shinn et al. (2023), we report performance
on 100 user instructions and use a different subset
of 40 queries as the dev set.
TextCraft. We create a new text-only environ-
ment for crafting Minecraft4 items similar to Word-
Craft (Coenen et al., 2021). Unlike existing agent-
based environments, tasks in TextCraft exhibit a
natural compositional structure, resembling cook-
ing recipes with steps of varying complexity, where
some sub-tasks are more intricate, such as layering
a lasagna, while others are simpler, like baking it.
Tasks in TextCraft are inherently decomposable.
In Fig. 3, crafting a beehive necessitates crafting
its ingredients, like planks and honeycomb, which
may require further decomposition. The agent thus
needs to identify and adapt to varying task com-
plexity, e.g., crafting a plank is easier than crafting
a beehive. Moreover, some recipes allow using any
item from a particular category. For instance, craft-
ing a beehive uses planks (a category), requiring
the agent to use linguistic knowledge for proper
item selection (e.g., select oak planks, a specific
item in the category planks). We evaluate our ap-
proach on a test set of 200 tasks where the target
items have recipe trees of depth 2, 3, and 4 (exam-
ple tree of depth 2 is shown in Fig. 3). We use the
4https://www.minecraft.net
5
