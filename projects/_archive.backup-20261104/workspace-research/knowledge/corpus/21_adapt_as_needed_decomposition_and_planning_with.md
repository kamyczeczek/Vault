---
type: Concept
id: 21_adapt_as_needed_decomposition_and_planning_with
title: "ADAPT: As-Needed Decomposition and Planning with Language Models (part 22/28)"
source: "ADAPT As-Needed Decomposition and Planning with Language Models.pdf"
tags: [LLM, Products, Think, agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

ALFWorld Planner Prompt
Here are some examples.
You are in the middle of a room. Looking quickly around you, you see a desk 1, microwave 1, a cabinet 3, a cabinet 9, a
drawer 2, a coffeemachine 1, a stoveburner 4, a drawer 5, a cabinet 11, a drawer 3, a stoveburner 1, a drawer 1, a
toaster 1, a fridge 1, a stoveburner 2, a cabinet 6, a cabinet 10, a countertop 1, a cabinet 13, a cabinet 7, a
garbagecan 1, a cabinet 2, a cabinet 8, a cabinet 12, a drawer 4, a cabinet 1, a sinkbasin 1, a cabinet 5, a
stoveburner 3, and a cabinet 4.
Goal: Put a mug in/on desk.
Come up with an abstract plan to perform this task in a couple of steps.
# Think: To perform this task, I need to find and take mug and then put it on desk. First, I will focus on finding mug.
Step 1: Find and take mug
# Think: Now that I am carrying mug, I will focus on putting it in/on desk.
Step 2: Put mug in/on desk
Execution Order: (Step 1 AND Step 2)
Goal: Clean mug and put it in/on desk.
Come up with an abstract plan to perform this task in a couple of steps.
# Think: To perform this task, I need to find and take mug, clean it, and then put it on desk. First, I will focus on
finding mug.
Step 1: Find and take mug
# Think: Now that I am carrying mug, I will focus on cleaning it.
Step 2: Clean mug with sinkbasin
# Think: Now that I have cleaned mug, I will focus on putting it in/on desk.
Step 3: Put cleaned mug in/on desk
Execution Order: (Step 1 AND Step 2 AND Step 3)
Goal: Cool mug and put it in/on desk.
Come up with an abstract plan to perform this task in a couple of steps.
# Think: To perform this task, I need to find and take mug, cool it, and then put it on desk. First, I will focus on
finding mug.
Step 1: Find and take mug
# Think: Now that I am carrying mug, I will focus on cooling it.
Step 2: Cool mug with fridge
# Think: Now that I have cooled mug, I will focus on putting it in/on desk.
Step 3: Put cooled mug in/on desk
Execution Order: (Step 1 AND Step 2 AND Step 3)
Goal: Heat mug and put it in/on desk.
Come up with an abstract plan to perform this task in a couple of steps.
# Think: To perform this task, I need to find and take mug, heat it, and then put it on desk. First, I will focus on
finding mug.
Step 1: Find and take mug
# Think: Now that I am carrying mug, I will focus on heating it.
Step 2: Heat mug with microwave
# Think: Now that I have heated mug, I will focus on putting it in/on desk.
Step 3: Put heated mug in/on desk
Execution Order: (Step 1 AND Step 2 AND Step 3)
Goal: Look at mug under desklamp.
Come up with an abstract plan to perform this task in a couple of steps.
# Think: To perform this task, I need to find and take mug, and then go to the desklamp and use it. First, I will focus on
finding mug.
Step 1: Find and take mug
# Think: Now that I have found and taken mug, I will focus on using the desklamp.
Step 2: Use the desklamp
Execution Order: (Step 1 AND Step 2)
Goal: Find and take mug
Come up with an abstract plan to perform this task in a couple of steps.
# Think: To perform this task I need to find mug in the room. mug is likely to be in desk, cabinet, countertop, or drawer.
Now I will focus on finding mug in each of these locations one by one.
Step 1: Find and take mug from desk
# Think: If mug not found so far, I will next look in the cabinet.
Step 2: Find and take mug from cabinet
# Think: If mug not found so far, I will next look in the countertop.
Step 3: Find and take mug from countertop
# Think: If mug not found so far, I will next look in the drawer.
Step 4: Find and take mug from drawer
Execution Order: (Step 1 OR Step 2 OR Step 3 OR Step 4)
Here is the goal.
<room>
Goal: <task>.
Come up with an abstract plan to perform this task in a couple of steps. Constraints: The robot can hold/take/put only one
object at a time to a location.
Ensure each step can be understood independently and mentions the name of object.
When stating the execution order, ensure that 'AND'/'OR' statements are properly nested using brackets '()'.
21
