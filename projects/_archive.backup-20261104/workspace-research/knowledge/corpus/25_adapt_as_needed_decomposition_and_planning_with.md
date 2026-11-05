---
type: Concept
id: 25_adapt_as_needed_decomposition_and_planning_with
title: "ADAPT: As-Needed Decomposition and Planning with Language Models (part 26/28)"
source: "ADAPT As-Needed Decomposition and Planning with Language Models.pdf"
tags: [LLM, Products, Think, agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

WebShop Planner Prompt
Write an abstract plan to successfully complete the goal. In each step of the plan mention which module (including
arguments) that need to be called. Learn from and incorporate information from previous runs, e.g. do not repeat
previously successful or unsuccesful commands. Here are some examples:Information from previous run: -
Goal: Buy 3 ounce bottle of citrus deodorant for sensitive skin, that is natural and priced less than 50.00 dollars.
# Think: Based on the criteria and the search bar, I should query 3 ounce citrus deodorant sensitive skin. I have the
following constraints: natural and price lower than $30 which I can use to narrow down search results.
Step 1: Search[3 ounce citrus deodorant sensitive skin]
# Think: Now I will need to narrow down the search results for price lower than $30 and natural
Step 2: SimpleMatch[3 ounce citrus deodorant sensitive skin with price lower than $50 and natural]
# Think: Since it returns a list of up to 3 products, I will pick the first suitable product. For now, Ill denote its id as
prod_id for placeholder.
Step 3: Buy[prod_id, "3 ounce bottle of citrus deodorant for sensitive skin, that is natural and priced less than 30.00
dollars"]
#Think: My plan requrires all these steps to succeed sequentially, so I will use the "AND" operator.
Execution Order: (Step 1 AND Step 2 AND Step 3)
Information from previous run:
- Unable to get matching product using: SimpleMatch[3 ounce citrus deodorant sensitive skin with price lower than $30 and
natural]
- Search results page:
[Back to Search]
Page 1 (Total results: 50)
[Next >]
[B078GWRC1J]
Bright Citrus Deodorant by Earth Mama | Safe for Sensitive Skin, Pregnancy and Breastfeeding, Contains Organic Calendula 3-
Ounce
$10.99
[B08KBVJ4XN]
Barrel and Oak - Aluminum-Free Deodorant, Deodorant for Men, Essential Oil-Based Scent, 24-Hour Odor Protection, Cedar &
Patchouli Blend, Gentle on Sensitive Skin (Mountain Sage, 2.7 oz, 2-Pack)
$35.95
[B078GTKVXY]
Ginger Fresh Deodorant by Earth Mama | Natural and Safe for Sensitive Skin, Pregnancy and Breastfeeding, Contains Organic
Calendula 3-Ounce
$10.99
[B08SMG4WB9]
Each & Every 2-Pack Natural Aluminum-Free Deodorant for Sensitive Skin with Essential Oils, Plant-Based Packaging (Citrus &
Vetiver, 2.5 Ounce (Pack of 2))
$25.0
[B08KVCCSD6]
Each & Every 3-Pack, Natural Aluminum-Free Deodorant for Sensitive Skin Made with Essential Oils, 2.5 Oz. (Lavender & Lemon,
Citrus & Vetiver, and Coconut & Lime)
$35.0
[B087WKSR2G]
Goal: Narrow down search results for 3 ounce bottle of citrus deodorant for sensitive skin that is priced lower than $30
and natural. You cannot search again.
#Think: Based on the search results and previous information, SimpleMatch failed because my criteria was too complex. Price
constraint is easy to verify, I will narrow down based on that first then examine in detail for natural constraint
#Think: Based on price, I narrow down my search to B078GWRC1J, B08SMG4WB9 as they look suitable. These are on my shortlist
to examine the natural constraint in detail one by one.
Step 1: DetailMatch[B078GWRC1J, 3 ounce bottle of for sensitive skin, that is natural and priced less than 30.00 dollars]
Step 2: DetailMatch[B08SMG4WB9, 3 ounce bottle of citrus deodorantcitrus deodorant for sensitive skin, that is natural and
priced less than 30.00 dollars]
#Think: If none of the products exactly match my criteria, I will search again with a new query that includes the natural
criteria too. This ensures my plan is compelete.
Step 3: Search[3 ounce citrus deodrant natural and sensitive skin]
#Think: Since these steps are linked by an if condition, I only need one of them to succeed. I will connect them using the
"OR" operator.
Execution Order: (Step 1 OR Step 2 OR Step 3)
Here is a new goal. Write an abstract plan to successfully complete the goal. In each step of the plan mention which module
(including arguments) that need to be called. Learn from and incorporate information from previous runs, e.g. do not
repeat previously successful or unsuccesful commands. In the end, output the intended execution order.
Information from previous run: {}
Goal: {}
25
