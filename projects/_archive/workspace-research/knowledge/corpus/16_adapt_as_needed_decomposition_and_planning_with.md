---
type: Concept
id: 16_adapt_as_needed_decomposition_and_planning_with
title: "ADAPT: As-Needed Decomposition and Planning with Language Models (part 17/28)"
source: "ADAPT As-Needed Decomposition and Planning with Language Models.pdf"
tags: [LLM, Products, Think, agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Webpage: [Search]
Task: I am looking to buy a product. i need a leak proof travel bottle that
is reusable and comes in 6 pack, and price lower than 30.00 dollars
Execute: Task
> search[leak proof reusable bottle]
Page:
[B0956WL7LT] ...
[B098XRX6M2] ...
> Think: Task failed!
Plan: Task
# Think: To do this task, ....
Step 1: Search "leak proof travel bottle reusable 6 pack"  AND
# Think: Now that I have found it, ....
Step 2: Match product on search page AND
# Think: Now that I have matched ....
Step 3: Buy matching product
Execute: Search "leak proof travel bottle reusable 6 pack"
> Think: Task completed!
Plan: Match product on search page
# Think: To do this task, ....
Step 1: Detail Match [B09...7LT] on product page OR
# Think: If that does not match, ....
Step 2: Detail Match [B08...GBG] on product page OR
# Think: If that does not match, ....
Step 3: Search "leak proof bottle reusable 6 pack $30"
Execute: Detail Match [B09...7LT] on product page
> Think: Task failed!
Execute: Detail Match [B08...GBG] on product page
> Think: Task completed!
Execute: Buy matching product
> Think: Task completed!
Matching Product:
[B08BGBPGBG]
...
...
   ADaPT (Adaptive Decomposition, Dynamic Depth)
......
...
Execute: Match product on search page
> Think: Task failed!
...
Search Results:
[B0956WL7LT] Portable Travel Bottles Set ...
[B08BGBPGBG] JND Plastic Squeeze Bottle ...
