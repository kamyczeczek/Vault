---
type: Concept
id: 71_icm_knowledge_big
title: "ICM_knowledge.md (part 72/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Return this as a markdown table with columns for Task, Owner, Deadline, and Status.

Write the first draft with [PLACEHOLDER] wherever I need to fill in company-specific details.

Give me the answer as a numbered list, then add a one-paragraph summary at the end.

Output format is the difference between getting something you can use immediately and getting something you have to reformat for 20 minutes.

------

When to use which parts

#### You do not need all five in every prompt. Here is the shortcut:

If your task is... You probably need... Simple and quick (rename this, fix this typo) Task only Creative (write this, design this) Identity + Task + Constraints + Output Format Complex (build this system, analyze this data) All five Ongoing (a project over many messages) Identity and Context in your folder files. Task and Constraints in each prompt.

Notice the last row. That is where the folder structure from 1.2 and this prompting framework connect. Your files carry the persistent stuff (identity, project context, rules). Your prompts carry the per-task stuff (what to do right now, what to avoid this time, what shape the output should take).

The folder is memory. The prompt is direction. They work together.

------

Chunking: breaking big projects into prompts

If your project is bigger than a single prompt can handle, break it into steps.

The rule: each prompt should ask for one clear thing.

#### Too much at once:

"Write me a full marketing strategy with a content calendar, email sequences, and social posts for the next quarter."

Claude will try to do all of it. The output will be shallow across the board because it is spreading its effort too thin.

#### Chunked into steps:

"Here is our product and audience. Outline the three main themes for Q2 content."

[You review. You adjust. You pick a direction.]

"Take theme 1 and draft a 4-week content calendar."

[You review. You adjust.]

"Write the first email in the nurture sequence for theme 1."

Each step builds on the last. You review and correct between steps. Claude gets cleaner input each time because you narrowed the scope. And if something goes wrong at step 3, you only redo step 3, not the whole thing.

This is the same principle behind the folder architecture. You do not dump everything into one giant file. You break it into layers. Prompting works the same way.

------

Chunking data: feeding Claude large inputs

If you need Claude to work with a long document, a big dataset, or a lot of source material, break the input too.

Give Claude the structure first.

"I am going to give you a 40-page report in sections. Here is the table of contents. I will send each section one at a time."

Feed sections in order. After each one, you can ask Claude to confirm what it picked up.

"Here is Section 3. What are the key claims in this section?"

After the last section, ask Claude to work across everything.
