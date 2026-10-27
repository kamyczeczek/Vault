---
type: Concept
id: 07_memory_for_autonomous_llm_agents_mechanisms_eval
title: "Memory for Autonomous LLM Agents: (part 8/15)"
source: "Memory for Autonomous LLM Agents Mechanisms, Evaluation, and Emerging Frontiers.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, icm, memory, planning, prompt-engineering, reflection, retrieval]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Table 2: Feature comparison of recent agent memory benchmarks.
Benchmark Year Multi-session Multi-turn Agentic tasks Forgetting Multimodal
LoCoMo 2024✓ ✓– –✓
MemBench 2025 –✓– – –
MemoryAgentBench 2025 –✓–✓–
MemoryArena 2026✓ ✓ ✓– –
via Ebbinghaus forgetting curves [Ebbinghaus, 1885]: fre-
quently accessed, high-importance memories are reinforced,
while neglected ones fade. MemGPT [Packer et al., 2024]
demonstrates multi-session chat with evolving user models.
The core tension in this domain ispersonalization without
overstepping—the agent must remember enough to be gen-
uinely helpful without surfacing information the user con-
siders private or forgotten.
6.2 Software engineering agents
Coding agents assist with generation, debugging, review,
and project management across codebases that may contain
millions of lines [Qian et al., 2024, Hong et al., 2024]. Mem-
ory requirements are steep: retain architecture decisions,
track bug report histories, remember code-style preferences,
and maintain a library of verified solutions. ChatDev [Qian
et al., 2024] equips role-playing agents (CEO, CTO, pro-
grammer, tester) with shared memory to keep a project
coherent across development phases. MetaGPT [Hong
et al., 2024] structures this shared memory as standardized
documents—PRDs, design specs, code modules—that per-
sist and evolve.
The distinguishing challenge here isstructural scale: the
memory system must index and retrieve relevant portions of
a codebase that may span thousands of files, not just conver-
sations.
6.3 Open-world game agents
Minecraft and similar sandboxes are popular testbeds pre-
cisely because they demand long-horizon planning and com-
positional skill reuse. V oyager [Wang et al., 2023a] showed
that an ever-growing skill library enables lifelong learning:
3.3×more unique items and 15.3×faster milestone progres-
sion than prior agents. JARVIS-1 [Wang et al., 2024b] ex-
tends this with multimodal memory spanning visual obser-
vations and textual plans. Ghost in the Minecraft [Zhu et al.,
2023] uses text-based knowledge and memory for generally
capable open-world agents.
The key challenge iscompositional skill reuse: the agent
must not only recall individual skills but chain them cre-
atively to solve novel problems.
6.4 Scientific reasoning and discovery
Scientific agents must track hypotheses, record experimen-
tal outcomes, digest literature, and revise beliefs as ev-
idence accumulates. Memory here acts as a hypothesis
ledger and evidence accumulator. The distinctive challenge
isuncertainty-aware memory: the agent must maintain not
just facts but confidence levels, and update them correctly as
new data arrives—something most current memory systems
handle poorly or not at all.
6.5 Multi-agent collaboration
When multiple agents work together, memory becomes a
coordination mechanism. AutoGen [Wu et al., 2023] lets
agents build on each other’s contributions through shared
context. CAMEL [Li et al., 2024] explores role-aware com-
municative agents that must remember prior agreements and
collaborative history. ProAgent [Zhang et al., 2024b] builds
proactive teammates that anticipate needs based on memory
of past interactions.
Two challenges dominate:shared vs. private memory
boundaries—what should be visible to whom?—andcon-
sistency under concurrent writes—what happens when two
agents update shared memory simultaneously? Current
multi-agent frameworks handle shared memory in one of
two ways: either all memory is shared (simple but leaks
private information) or each agent maintains its own store
with no cross-agent access (isolated but prevents knowledge
transfer). Neither extreme is satisfactory. A principled mid-
dle ground would define role-based access controls over a
shared memory substrate, allowing a project manager agent
to see high-level summaries from a developer agent without
accessing the raw code diffs. Database-style access control
lists, adapted for natural language records, are a natural but
unexplored solution.
6.6 Tool use and API orchestration
Tool-using agents [Schick et al., 2024] interact with APIs,
databases, and web services. Memory must track which
tools exist, how to call them, what parameters worked
last time, and which sequences of calls have been veri-
fied. AgentBench [Liu et al., 2023] evaluates agents across
eight environments; agents that lose track of their command
history show sharp performance drops in multi-step tasks.
DERA [Nair et al., 2023] uses dialog-turn memory to refine
tool-use strategies iteratively.
A practical hazard unique to this setting isschema drift:
when an API updates its interface, stored usage patterns be-
come invalid. Version tracking and schema validation on
stored tool-use records are essential but rarely implemented.
In fast-moving API ecosystems, a tool-use memory system
that does not handle schema drift will accumulate an in-
creasing fraction of invalid records, progressively degrading
the agent’s ability to reuse past experience.
The broader point here is that tool-use memory is not
just about storing “what worked”; it is about maintaining
a living, versioned catalog of tool capabilities that degrades
gracefully as the external world changes. This connects to
8
