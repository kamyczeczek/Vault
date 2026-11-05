---
type: Concept
id: 24_adapt_as_needed_decomposition_and_planning_with
title: "ADAPT: As-Needed Decomposition and Planning with Language Models (part 25/28)"
source: "ADAPT As-Needed Decomposition and Planning with Language Models.pdf"
tags: [LLM, Products, Think, agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

WebShop Executor Prompt: Shortlist (cont.)
You are given a search page on an online shopping site with a list of products along with name and price. Based on this
information, your task is return a list of product IDs (enclosed in []) of all products that exactly match all
requirements in the criteria. If the information provided is not enough to make a determination, return an empty list.
Here are a few examples.
Search Page:
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
Criteria: less than 5 ounce citrus deodorant sensitive skin, price less than $30.
Answer: My requirements are 5 ounce, citrus deodrant, suitable for sensitive skin, and price less than $30. Looks like this
information is available on the search page, so I can proceed.
Products B078GWRC1J, B08SMG4WB9 look suitable as they are less than 5 ounce, citrus and have price 10.99 and $25 less than
$30. Thus, shortlisted IDs are shortlisted=[ 'B078GWRC1J', 'B08SMG4WB9']
Criteria: less than 5 ounce citrus deodorant sensitive skin, cruelty free.
Answer: My requirements are 5 ounce, citrus deodrant, suitable for sensitive skin, and cruelty-free. Since there is no
information about cruelty free on the search page, I cannot proceed. Task failed!
Here is another task with a different search page and criteria. List all the product ids (enclosed in []) from the search
page that match ALL the requirements in the criteria. Name this list shortlisted. If you cannot make the
determination about even 1 sub-criteria, do not make a guess, output "task failed!". Generate an explanation before
the answer to justify your decision.
Search Page:
{}
Criteria: {}
Answer:
24
