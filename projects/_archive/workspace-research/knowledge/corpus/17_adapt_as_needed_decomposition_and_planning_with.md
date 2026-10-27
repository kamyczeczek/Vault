---
type: Concept
id: 17_adapt_as_needed_decomposition_and_planning_with
title: "ADAPT: As-Needed Decomposition and Planning with Language Models (part 18/28)"
source: "ADAPT As-Needed Decomposition and Planning with Language Models.pdf"
tags: [LLM, Products, Think, agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Prev: Failed Match product on search page
...
Figure 10: Partial rolled out trajectories for WebShop
with ADAPT. In the gray box we communicate to the
planner the current (search) page that is visible to the
agent, and once a matching product is found, we propa-
gate it to future executor runs. Note “match on search
page” corresponds to shortlist skill in Table 5, and “de-
tail match on product page” corresponds to match skill.
agent’s inventory. An illustrative gold trajectory
from TextCraft is shown in Fig. 3.
We create the TextCraft environment using
Minecraft v1.16.5 recipes. We only consider the
recipes craftable using a crafting table. We consider
both shapeless (only count matters) and shaped
(position of ingredients matters) recipes and con-
vert them into crafting commands (e.g. craft 4
sticks using 2 planks ). Items that do not have
any recipe are considering obtainable via the get
command, e.g. get 4 diamond .
Since the entire set of crafting commands would
not fit in the context of modern LLMs, we create
Crafting Commands:
craft andesite slab using 3 andesite
craft 2 andesite using 1 diorite, 1 cobblestone
craft 6 diorite wall using 6 diorite
craft 2 diorite using 2 quartz, 2 cobblestone
Task: craft andesite slab
Execute: craft andesite slab
> get 3 andesite
Could not execute: get 3 andesite
> get 1 diorite
Could not execute: get 1 diorite
> Think: Task failed!
Plan: craft andesite slab
# Think: To do this task, ....
Step 1: Fetch 3 andesite  AND
# Think: Now that I have found it, ....
Step 2: Craft andesite slab using 3 andesite
Execute: Fetch 3 andesite
> Think: Task failed!
Plan: Fetch 3 andesite
# Think: To do this task, ....
Step 1: Fetch 1 diorite AND
# Think: Fetch the next ingredient, ....
Step 2: Fetch 1 cobblestone AND
# Think: Now that I have found, ....
Step 3: Craft 2 andesite using 1 diorite, 1 cobblestone AND
# Think: Since I need 3 andesite, ....
Step 4: Craft 2 andesite using 1 diorite, 1 cobblestone
Execute: Fetch 1 diorite
> Think: Task completed!
Execute: Fetch 1 cobblestone
> Think: Task completed!
Execute: Craft andesite slab using 3 andesite
> Think: Task completed!
...
...
   ADaPT (Adaptive Decomposition, Dynamic Depth)
......
...
...
Inventory: [diorite] (2)
Inventory: [diorite] (2), [cobblestone] (1)
Execute:  Craft 2 andesite using 1 diorite, 1
cobblestone
> Think: Task completed!
...
Inventory: [diorite] (1), [cobblestone] (1), [andesite] (2)
Execute:  Craft 2 andesite using 1 diorite, 1
cobblestone
> Think: Task completed!
Inventory: [andesite] (4)
Figure 11: Partial rolled out trajectories for TextCraft
using ADAPT. In the gray box, we propagate the in-
ventory of the agent to subsequent executor calls. Note
that while “diorite” is not directly present in the envi-
ronment, i.e., it needs to be crafted. The executor LLM
is able to inherently compose skills to fetch it without
further decomposition.
a set of relevant crafting commands for every task.
Apart from the set of gold crafting commands (i.e,
crafting commands for all the items in the recipe
tree), we also add up to 10 distractor commands.
To create this distractor set, we sub-sample up to
10 recipes for every ingredient in the recipes of our
gold recipe tree. We finally sub-sample up to 10
distractors from this entire set to ensure a reason-
17
