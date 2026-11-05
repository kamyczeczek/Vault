---
type: Concept
id: 23_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 24/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Sesame Oil
Garlic
Ginger
C.3 Domain: Blocks World
C.3.1 Problem Specification
I am playing with a set of blocks where I need to arrange the blocks into stacks.
Here are the actions I can do:,→
Pick up a block
Unstack a block from on top of another block
Put down a block
Stack a block on top of another block
I have the following restrictions on my actions:
I can only pick up or unstack one block at a time.
I can only pick up or unstack a block if my hand is empty.
I can only pick up a block if the block is on the table and the block is clear.
A block is clear if the block has no other blocks on top of it and if the
block is not picked up.
,→
,→
I can only unstack a block from on top of another block if the block I am
unstacking was really on top of the other block.,→
I can only unstack a block from on top of another block if the block I am
unstacking is clear.,→
Once I pick up or unstack a block, I am holding the block.
I can only put down a block that I am holding.
I can only stack a block on top of another block if I am holding the block being
stacked.,→
I can only stack a block on top of another block if the block onto which I am
stacking the block is clear.,→
Once I put down or stack a block, my hand becomes empty.
Once you stack a block on top of a second block, the second block is no longer
clear.,→
Please provide a plan as a list of actions with space deliminated arguments line
by line in the following format in answer.txt:,→
pick [block]: pick a block up
put [block]: put a block down
stack [block1] [block2]: stack block1 on block2
unstack [block1] [block2]: unstack block1 from on top of block2
An example plan:
unstack blue red
put blue
pick red
stack red green
Write an answer to answer.txt. The plan will be checked automatically so please
follow the above format. The only actions allowed are [pick, put, stack,
unstack].
,→
,→
27
