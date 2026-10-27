---
type: Concept
id: 19_adapt_as_needed_decomposition_and_planning_with
title: "ADAPT: As-Needed Decomposition and Planning with Language Models (part 20/28)"
source: "ADAPT As-Needed Decomposition and Planning with Language Models.pdf"
tags: [LLM, Products, Think, agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

ALFWorld Hybrid Executor Prompt
Here is a demo of actions you can perform.
You are in the middle of a room. Looking quickly around you, you see a desk 1, microwave 1, a cabinet 3, a cabinet 9, a
drawer 2, a coffeemachine 1, a stoveburner 4, a drawer 5, a cabinet 11, a drawer 3, a stoveburner 1, a drawer 1, a
toaster 1, a fridge 1, a stoveburner 2, a cabinet 6, a cabinet 10, a countertop 1, a cabinet 13, a cabinet 7, a
garbagecan 1, a cabinet 2, a cabinet 8, a cabinet 12, a drawer 4, a cabinet 1, a sinkbasin 1, a cabinet 5, a
stoveburner 3, and a cabinet 4.
Your task is to: Put a tomato in cabinet 1.
> think: Input assumption: I am carrying a tomato. Now I need to verify this.
OK.
> inventory
You are carrying: a tomato 1.
> examine tomato 1
There's nothing special about tomato 1.
> think: Based on previous context assumption is true, now I can proceed.
> go to cabinet 1
The cabinet 1 is closed.
> open cabinet 1
You open the cabinet 1. The cabinet 1 is open. In it, you see a candle 1, and a spraybottle 2.
> put tomato 1 in/on cabinet 1
You put the tomato 1 in/on the cabinet 1.
> think: End state: Now I put tomato (1) in cabinet (1). Task completed!
Your task is to: Take a mug from cabinet 5
> think: Input assumption: None
OK.
> go to cabinet 5
The cabinet 5 is closed.
> open cabinet 5
You open the cabinet 5. The cabinet 5 is open. In it, you see a mug 3.
> take mug 3 from cabinet 5
You pick up the mug 3 from the cabinet 5.
> think: End state: Now I take a mug (3) from cabinet (5). Task completed!
Your task is to: Heat an egg.
> think: Input assumption: I am carrying an egg. Now I need to verify this.
OK.
> inventory
You are carrying: a egg 2.
> examine egg 2
There's nothing special about egg 2.
> think: Based on previous context assumption is true, now I can proceed.
OK.
> go to microwave 1
The microwave 1 is closed.
> heat egg 2 with microwave 1
You heat the egg 2 using the microwave 1.
> think: End state: Now I heat a egg (2). Task completed!
Your task is to: Cool a mug.
> think: Input assumption: I am carrying a mug. Now I need to verify this.
OK.
> inventory
You are carrying: a mug 3.
> examine mug 3
There's nothing special about mug 3.
> think: Based on previous context assumption is true, now I can proceed.
OK.
> go to fridge 1
The fridge 1 is closed.
> cool mug 3 with fridge 1
You cool the mug 3 using the fridge 1.
> think: End state: Now I cool a mug (3). Task completed!
Your task is to: Clean a lettuce.
> think: Input assumption: I am carrying a lettuce. Now I need to verify this.
OK.
> inventory
You are carrying: a lettuce 1.
> examine lettuce 1
There's nothing special about lettuce 1.
> think: Based on previous context assumption is true, now I can proceed.
OK.
> go to sinkbasin 1
On the sinkbasin 1, you see a apple 2, a ladle 2, a spoon 1, and a tomato 3.
> clean lettuce 1 with sinkbasin 1
You clean the lettuce 1 using the sinkbasin 1.
> think: End state: Now I clean a lettuce (1). Task completed!
19
