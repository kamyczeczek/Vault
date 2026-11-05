---
type: Concept
id: 02_memory_for_autonomous_llm_agents_mechanisms_eval
title: "Memory for Autonomous LLM Agents: (part 3/15)"
source: "Memory for Autonomous LLM Agents Mechanisms, Evaluation, and Emerging Frontiers.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, icm, memory, planning, prompt-engineering, reflection, retrieval]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

2.4 Memory as a differentiator: an empirical
perspective
The practical importance of memory design is perhaps best
illustrated by ablation results reported across recent systems.
In the Generative Agents experiment [Park et al., 2023],
removing the reflection component caused agent behavior
to degenerate from coherent multi-day planning to repeti-
tive, context-free responses within 48 simulated hours. V oy-
ager [Wang et al., 2023a] without its skill library lost 15.3×
in tech-tree milestone speed—the skill librarywasthe per-
formance. And in MemoryArena [He et al., 2026], swap-
ping an active memory agent for a long-context-only base-
line dropped task completion from over 80% to roughly 45%
on interdependent multi-session tasks.
These numbers underscore a recurring theme: the gap be-
tween “has memory” and “does not have memory” is often
larger than the gap between different LLM backbones. In-
vesting in memory architecture can yield returns that rival—
or exceed—model scaling.
3 A Unified Taxonomy of Agent
Memory
Cognitive scientists have long distinguished multiple mem-
ory systems in the human brain [Atkinson and Shiffrin,
1968, Tulving, 1972, Baddeley, 2000, Squire, 2004]. Agent
designers—often unconsciously—mirror that structure. We
organize the space along three orthogonal dimensions.
3.1 Temporal scope
Working memory.Whatever fits inside the current context
window constitutes the agent’s working memory. Badde-
ley’s central executive plus buffer model [Baddeley, 2000]
maps neatly: the LLM is the executive, the context window
is the buffer, and both share the same bottleneck—limited
capacity.
Episodic memory.Records of concrete experiences: in-
dividual tool calls, conversation turns, environment obser-
vations. In the Generative Agents world [Park et al., 2023],
every observation—“Isabella saw Klaus painting in the park
at 3pm”—lands in the episodic stream with a timestamp, an
importance score, and an embedding for later retrieval.
Semantic memory.Abstracted, de-contextualized
knowledge. An episodic fact like “the user corrected the date
format on Jan 5, Jan 12, and Feb 1” may consolidate into the
semantic record “user prefers DD/MM/YYYY .” This con-
solidation is rarely automatic; most current systems require
explicit prompting or heuristic triggers.
Procedural memory.Reusable skills and executable
plans. V oyager’s skill library [Wang et al., 2023a] is the
clearest example: every verified Minecraft routine is stored
as runnable JavaScript, indexed by a natural language de-
scription, and composed on the fly for novel tasks.
In practice, most agents blend at least two of these. The
hard question is thetransition policy: when does an episodic
record graduate to semantic status, and when does a seman-
tic fact get instantiated back into working memory for a spe-
cific task?
To illustrate the interplay, consider a customer-support
agent handling returns. Each return request constitutes an
episodic record. After processing hundreds of similar re-
quests, the agent might consolidate the pattern into a seman-
tic rule: “customers who received damaged items within 7
days are eligible for express replacement.” When a new
request arrives, this semantic rule is loaded into working
memory alongside the specific episodic details of the cur-
rent case. If the agent also has stored scripts for processing
returns (procedural memory), the four memory types form a
complete reasoning stack: the procedure sayshow, seman-
tic memory sayswhat the policy is, episodic memory says
what happened, and working memory holds the live reason-
ing context.
This four-layer integration is the aspiration; most current
systems implement only two layers well and handle the tran-
sitions between layers via crude heuristics. The consolida-
tion step—where episodes become semantic knowledge—
is particularly underserved: it typically requires either ex-
plicit developer rules or periodic LLM-driven summariza-
tion, both of which are fragile and hard to validate.
3.2 Representational substrate
How memory is physically stored constrains what the agent
can efficiently do with it.
Context-resident text—summaries, scratchpads, chain-
of-thought traces [Wei et al., 2022]—is the simplest sub-
strate. Fully transparent, zero infrastructure, but ruthlessly
capacity-limited.
Vector-indexed storesencode records as dense em-
beddings and support approximate nearest-neighbor
search [Karpukhin et al., 2020, Johnson et al., 2021]. They
scale gracefully to millions of records but lose structured
relationships: you can ask “what’s most similar?” but not
“what caused what?”
Structured stores—SQL databases [Hu et al., 2023],
key–value maps, knowledge graphs [Ji et al., 2022]—
preserve relational structure and support complex queries
(“all API failures involving service X in the last 7 days”),
at the cost of upfront schema design.
Executable repositories—code libraries, tool defini-
tions, plan templates [Wang et al., 2023a]—let the agent in-
voke stored skills directly, sidestepping regeneration and the
errors it introduces.
Hybrid storesare the norm in production.
MemGPT [Packer et al., 2024], for instance, layers a
context-window “main memory” over a searchable recall
database and a vector-indexed archive—each tier with
different access patterns and eviction rules.
3.3 Control policy
Perhaps the most consequential—and least discussed—
dimension iswho decideswhat to store, what to retrieve,
and what to discard.
Heuristic controlhard-codes rules: top-kretrieval, sum-
marize everynturns, expire records older thanddays. Pre-
dictable, easy to debug, but blind to context.
Prompted self-controlexposes memory operations
as tool calls and lets the LLM decide when to in-
voke them. MemGPT’score_memory_appendand
3
