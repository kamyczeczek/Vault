---
type: Concept
id: 22_adapt_as_needed_decomposition_and_planning_with
title: "ADAPT: As-Needed Decomposition and Planning with Language Models (part 23/28)"
source: "ADAPT As-Needed Decomposition and Planning with Language Models.pdf"
tags: [LLM, Products, Think, agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

WebShop Executor Prompt: Buy
Instruction: Buy product [B078GWRC1J] that matches criteria: 3 ounce bottle of bright citrus deodorant for sensitive skin,
and price lower than 50.00 dollars
Action: think[ 'I should be on the search page where I can see a list of products, I should verify that. ']
Observation: OK.
Action: load
Observation:
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
Action: think[ 'I can spot product [B078GWRC1J] and it is a clickable link since its enclosed in square brackets. I should
click on it.]
Observation: OK.
Action: click[B078GWRC1J]
Observation:
[Back to Search]
[< Prev]
scent [assorted scents][bright citrus][calming lavender][ginger fresh][simply non-scents]
size [travel set (4-pack)][3 ounce (pack of 1)][3-ounce (2-pack)]
Bright Citrus Deodorant by Earth Mama | Natural and Safe for Sensitive Skin, Pregnancy and Breastfeeding, Contains Organic
Calendula 3-Ounce
Price: $10.99
Rating: N.A.
[Description]
[Features]
[Reviews]
[Buy Now]
Action: think[I 'm already on the product page. I see multiple possible options enclosed in '[]' for scent and size for this
product. To match the input criteria, I should click on options '[bright citrus] ' for scent and '[3 ounce (pack of 1)
]' for size one by one and then buy in the end.]
Observation: OK.
Action: click[bright citrus]
Observation: You have clicked bright citrus.
Action: click[3 ounce (pack of 1)]
Observation: You have clicked 3 ounce (pack of 1).
Action: think[My task is to buy the product, for it should to click 'buy now ']
Observation: OK.
Action: click[Buy Now]
Observation: You have clicked buy now.
Action: think[I finished buying the product. Task completed!]
Here is another task in which you need to buy a product. When you finish buying the product with the most relevant choices,
use 'think[Task completed ']. If you cannot find the matching options or proceed, think[ 'Task failed ']. Note that you
can only click on text enclosed in '[]' on the webpage. Everything else is only a description, not valid with the "
click" action.
Instruction: Buy product [{}] that matches the criteria: {}
22
