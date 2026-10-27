---
type: Concept
id: 15_adapt_as_needed_decomposition_and_planning_with
title: "ADAPT: As-Needed Decomposition and Planning with Language Models (part 16/28)"
source: "ADAPT As-Needed Decomposition and Planning with Language Models.pdf"
tags: [LLM, Products, Think, agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Room: You are in the middle of a room. Looking quickly around you, you
see a cabinet 21, a cabinet 20, a cabinet 19, a cabinet 18, a cabinet 17,
a cabinet 16, a cabinet 15, a cabinet 14, a cabinet 13, a cabinet 12, a
cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet
6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a
coffeemachine 1, a countertop 2, a countertop 1, a diningtable 1, a
drawer 5, a drawer 4, a drawer 3, a drawer 2, a drawer 1, a fridge 1, a
garbagecan 1, a microwave 1, a sinkbasin 1, a stoveburner 4, a
stoveburner 3, a stoveburner 2, a stoveburner 1, desk 1, and a toaster 1.
Your task is to: Put a clean mug on desk.
Execute: Put a clean mug on desk
> Go to countertop 1
You reached loc 1, ...
> Go to countertop 2
You reached loc 2, ...
> Think: Mug not found, task failed!
Plan: Put a clean mug on desk
# Think: To do this task, ....
Step 1: Find and take the mug AND
# Think: Now that I have found it, ....
Step 2: Clean the mug using sinkbasin AND
# Think: Now that I have cleaned ....
Step 3: Put clean mug on desk
Execute: Find and take the mug
> Think: Task failed!
Plan: Find and take the mug
# Think: To do this task, ....
Step 1: Find and take mug from countertop OR
# Think: If I do not find the mug, ....
Step 2: Find and take mug from cabinet OR
# Think: If I do not find the mug, ....
Step 3: Find and take mug from drawer
Execute: Find and take mug from countertop
> Think: Task failed!
Execute: Find and take mug from cabinet
> Think: Task completed!
Execute: Clean the mug using sinkbasin
> Think: Task completed!
Execute: Find and take the mug from countertop
> Think: Task completed!
Previously executed:
> take mug 1 from cabinet 7
You picked up mug 1
...
...
Room: You are in the middle of a room. Looking quickly around you, you
see a cabinet 21, a cabinet 20, a cabinet 19, a cabinet 18, a cabinet 17,
a cabinet 16, a cabinet 15, a cabinet 14, a cabinet 13, a cabinet 12, a
cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet
6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a
coffeemachine 1, a countertop 2, a countertop 1, a diningtable 1, a
drawer 5, a drawer 4, a drawer 3, a drawer 2, a drawer 1, a fridge 1, a
garbagecan 1, a microwave 1, a sinkbasin 1, a stoveburner 4, a
stoveburner 3, a stoveburner 2, a stoveburner 1, desk 1, and a toaster 1.
Your task is to: Put a clean mug on desk.
Execute: Put a clean mug on desk
> Think: To solve the task, I need to find and take a mug, then clean it
with sinkbasin, then put on the desk.
OK.
> Think: First I need to find a mug. A mug is more likely to appear in
fridge (1), countertop (1-2), dining table (1), cabinet (1-21), drawer
(1-5). I can check one by one, starting with fridge 1.
OK.
> open fridge 1
Nothing happens.
> go to fridge 1
You arrive at loc 15, fridge 1 is closed.
> open fridge 1
        You open the fridge 1. The fridge 1 is open. In it, you see a bowl 1, a
cup 1, a egg 1, a lettuce 1, a plate 1, and a tomato 1.
> Think: There is no mug in fridge 1, I need to go to countertop 1 next.
OK.
> go to countertop 1
You reached loc 1, on it you see a cd 2, a cellphone 3, a
cellphone 1, a keychain 3, a pen 2, a pencil 3 and a pencil 2.
> go to countertop 2
    You reached loc 2, on it you see a egg 3, a knife 2, a knife 1, a potato
1, a potato 2, a bread 1, a dishsponge 3, and a saltshaker 1.
> Think: There is no mug in countertop 2, I need to go to cabinet 1.
OK.
> go to cabinet 1
You arrive at loc 4, cabinet 1 is closed.
> open cabinet 1
                    You open cabinet 1. Cabinet 1 is open. In it, you see bowl 3,
fork 2, soapbottle 1, and a cloth 1.
> go to cabinet 2
You arrive at loc 5, cabinet 2 is closed.
> open cabinet 2
You open cabinet 2. Cabinet 2 is open. In it, you see nothing.
> open cabinet 4
Nothing happens.
> go to cabinet 4
You arrive at loc 7, cabinet 4 is closed.
> open cabinet 4
        You open cabinet 4. Cabinet 4 is open. In it, you see a spatula 1, a
cloth 2, a peppershaker 1, cup 3, a apple 2, and a toiletpaper 1.
> take mug 3 from cabinet 4
Nothing happens.
> take cup 3 from cabinet 4
You pick up cup 3 from cabinet 4
> Think: Now I found cup (3). Next I need to clean it. For this ...
...
   ADaPT (Adaptive Decomposition, Dynamic Depth)Iterative Executor (ReAct)
......
......
Figure 9: Comparison of iterative executors such as ReAct with ADAPT. On left, ReAct uses interleaved “thought”
statements to set milestones and track their progress. However, due to a large action history, it struggles to follow
the plan exactly and hallucinates the wrong object (highlighted in red). ADAPT, on the right, decomposes complex
tasks into smaller sub-tasks whenever the executor fails, leading to shorter action trajectories for easy execution.
ReAct baseline. The difference in ReAct perfor-
mance for both settings corroborates our hypothesis
that increasing number of products on the search
page increases task complexity, all else equal. No-
tably, we show thatADAPT yields higher improve-
ment for more complex task settings.
E TextCraft
TextCraft: Environment Details. In TextCraft,
the objective is to obtain target Minecraft items
by crafting them from available items in the envi-
ronment. We define an environment with three ac-
tions: craft <item> using <ingredients> , get
<item>, and inventory. We utilize Minecraft’s
crafting recipes to specify craftable items and their
ingredients, assuming that all other items are ob-
tainable from the environment. Similar to Alf-
World, our agent can directly execute these op-
erations in the embodied game. The game begins
with a list of crafting commands provided to the
agent that detail recipes that can be used to craft
the final target, its ingredients along with some dis-
tractors (details in Appendix E). A reward of 1 is
generated when the target item gets added to the
16
