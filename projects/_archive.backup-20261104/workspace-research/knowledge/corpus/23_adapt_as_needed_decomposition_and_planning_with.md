---
type: Concept
id: 23_adapt_as_needed_decomposition_and_planning_with
title: "ADAPT: As-Needed Decomposition and Planning with Language Models (part 24/28)"
source: "ADAPT As-Needed Decomposition and Planning with Language Models.pdf"
tags: [LLM, Products, Think, agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

WebShop Executor Prompt: Match (cont.)
You are given a webpage of an item on an online shopping website and a criteria. Your task is to answer if the product on
the page exactly matches the criteria. Not the criteria could have multiple requirements that should be checked one
by one and all must satisfy for an exact match.
Here are a few examples:
Criteria: 3 ounce bottle of citrus deodorant for sensitive skin that is priced lower than $30 and natural.
Item Page:
[Back to Search]
[< Prev]
scent [assorted scents][bright citrus][calming lavender][ginger fresh][simply non-scents]
size [travel set (4-pack)][3 ounce (pack of 1)][3-ounce (2-pack)]
Bright Citrus Deodorant by Earth Mama | Natural and Safe for Sensitive Skin, Pregnancy and Breastfeeding, Contains Organic
Calendula 3-Ounce
Price: $10.99
Rating: N.A.
[Description]
Features:
NEW from Earth Mama (formerly Earth Mama Angel Baby), formulated especially for pregnancy, breastfeeding and sensitive
skin
Contains organic grapefruit, tangerine and calendula
NO propylene glycol, artificial fragrance, parabens or aluminum
Dermatologist tested and clinically tested for irritation
Better than natural organic! NSF/ANSI 305 Certified by Oregon Tilth
[Reviews]
[Attributes]
[Buy Now]
Answer: The product is available in 3 ounce size, is citrus and suitable for sensitive skin. It is also organic or natural.
Its price is $10.99 which is less than $30.
Thus, the answer is True (exact match).
Criteria: 3 ounce bottle of citrus deodorant for sensitive skin that is priced lower than $30 and natural.
Item Page:
[Back to Search]
[< Prev]
size [3 ounce][3 ounce (pack of 1)]
unit count [2.0][3.0]
Barrel and Oak - Aluminum-Free Deodorant, Deodorant for Men, Essential Oil-Based Scent, 24-Hour Odor Protection, Cedar &
Patchouli Blend, Gentle on Sensitive Skin (Mountain Sage, 2.7 oz, 2-Pack)
Price: $15.95
Rating: N.A.
[Description]
Features:
About this item WHY ALUMINUM-FREE DEODORANT? Aluminum-free deodorants use more natural ingredients unlike antiperspirants,
which use chemicals to block sweat. Safely fight odor for 24 hours with Barrel & Oak 's deodorantsour gentle formula
is easy on sensitive skin. START SMELLING LIKE THE MAN YOU WANT TO BE: Our mountain sage aluminum-free men 's
deodorant is naturally fragranced with an outdoorsy scent of crisp conifer, sage, & citrus. Think sweet notes of
citrus with earthy tones of cedar & patchouli. PREMIUM INGREDIENTS FOR NATURAL FRAGRANCES: Our deodorants for men are
composed of natural, essential oil-based scents. These natural fragrance deodorants are more subtle than their
synthetic counterparts, but they 're better for you & the planet. DESIGNED FOR THE MODERN MAN: Barrel & Oak has a full
spectrum of grooming & body care products that are designed with function, fragrance, & effective ingredients for
the health-conscious & practical modern man. Give your body what it deserves. EARTH-FRIENDLY, YOU-FRIENDLY, WALLET-
FRIENDLY: Our premium products for men are scented with natural fragrances & essential oils, free of parabens,
phthalates, & SLS, packaged in recyclable materials, cruelty-free, & vegan or vegetarian.
[Reviews]
[Attributes]
[Buy Now]
Answer: The product is not citrus in nature. It does not match the criteria. It 's price is $15.95 which is less than $30.
Thus, the answer is False (not an exact match).
Now here is the criteria and item page for the another task. Try you best to determine exact match, otherwise, respond with
"False", i.e., no exact match. Generate an explanation before the answer to justify your decision.
Criteria: {}
Item Page:
{}
Answer:
23
