---
type: Concept
id: 12_adapt_as_needed_decomposition_and_planning_with
title: "ADAPT: As-Needed Decomposition and Planning with Language Models (part 13/28)"
source: "ADAPT As-Needed Decomposition and Planning with Language Models.pdf"
tags: [LLM, Products, Think, agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Shunyu Yao, Howard Chen, John Yang, and Karthik
Narasimhan. 2022. Webshop: Towards scalable real-
world web interaction with grounded language agents.
Advances in Neural Information Processing Systems,
35:20744–20757.
Shunyu Yao, Dian Yu, Jeffrey Zhao, Izhak Shafran,
Thomas L Griffiths, Yuan Cao, and Karthik
Narasimhan. 2023a. Tree of thoughts: Deliberate
problem solving with large language models. arXiv
preprint arXiv:2305.10601.
Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak
Shafran, Karthik R Narasimhan, and Yuan Cao.
2023b. React: Synergizing reasoning and acting
in language models. In The Eleventh International
Conference on Learning Representations.
Jesse Zhang, Haonan Yu, and Wei Xu. 2021. Hierarchi-
cal reinforcement learning by discovering intrinsic
options. In International Conference on Learning
Representations.
Wenqing Zheng, SP Sharan, Ajay Kumar Jaiswal, Kevin
Wang, Yihan Xi, Dejia Xu, and Zhangyang Wang.
2023. Outline, then details: Syntactically guided
coarse-to-fine code generation. In International Con-
ference on Machine Learning, pages 42403–42419.
PMLR.
Andy Zhou, Kai Yan, Michal Shlapentokh-Rothman,
Haohan Wang, and Yu-Xiong Wang. 2023. Lan-
guage agent tree search unifies reasoning acting
and planning in language models. arXiv preprint
arXiv:2310.04406.
A AD APT Implementation Details
Executor. We use a common ReAct executor for
each dataset. To this end, we provide the LLM
in the executor with in-context example trajecto-
ries for each atomic skill (refer to Table 5 for an
exhaustive list). Atomic skills are inherently task
dependent, and thus, vary with the underlying envi-
ronment. For ALFWorld, in which the agent needs
to navigate and perform tasks in the household, the
atomic skills include: taking an object, putting it
down at a location, cleaning, heating, etc. On the
other hand, the goal in WebShop is to buy a product
based on user queries, thus, atomic skills include:
searching a specified query, shortlisting products
based on search page, matching if a product sat-
isfies a criteria, and buying a product. Lastly, the
atomic skills in TextCraft are fetching objects from
the environment, and crafting them given the recipe
and the ingredients. Following Yao et al. (2023b),
we add gold trajectories for two tasks: heat and
look in the executor prompt for ALFWorld, and
one full gold trajectory for TextCraft.
Atomic Skill Description
ALFWorld
put Assuming that the robot is carrying
an object, put it on a given receptacle.
take Take a specified object from a speci-
fied receptacle.
clean/heat/cool Assuming that the robot is carrying
an object, clean/heat/cool the object.
examine Assuming the robot is at a desk with a
desk lamp, use it to look at an object.
WebShop
search Put a given query in the search box,
results in a page with list of products.
shortlist Based on the search page and query,
get list of any matching products.
match Given a product ID and query, navi-
gate to the product page and verify it
matches the query.
buy Given a product ID and query, buy
product by selecting relevant options.
TextCraft
craft Assuming the agent has all the ingre-
dients in the inventory, craft a target
object by picking an appropriate com-
mand from the list of crafting recipes.
fetch Look for a given object in the inven-
tory or get it directly from the game.
inventory Look-up the game inventory.
Table 5: Overview of atomic skills used in Sec. 3.1.
Planner. We provide the LLM with a brief de-
scription of atomic skills and in-context demonstra-
tions of few task decompositions for each dataset.
• ALFWorld: The planner includes 6 demonstra-
tions of task decompositions for one household
configuration. Specifically, “find” is not an
atomic skill for the executor, and therefore, needs
to be handled by the planner (refer to Fig. 2).
• WebShop: The planner breaks down a given task
in terms of the atomic skills described in Table 5
via 2 in-context demonstrations.
• TextCraft: The planner determines the necessary
ingredients for each item and creates a plan to
obtain them and then craft the item, illustrated
via 2 examples with different crafting commands.
Controller. The controller performs two crucial
roles in the overall functioning of ADAPT. First, it
serves as the communication bridge between plan-
ner and executor, propagating salient information
across the two depending on the task. Second, since
ADAPT is a recursive algorithm, the controller de-
termines the termination criterion using the logical
expression from the planner and success heuristic
from the executor or if a maximum depth dmax
(≥1) is reached. The controller propagates task-
dependent salient information described below:
• ALFWorld: In the controller, we propagate the
last successful action from a previous execution
13
