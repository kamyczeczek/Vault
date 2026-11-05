---
type: Concept
id: 02_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 3/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

chaining and memory-augmented reasoning for open-ended tasks, while frameworks such as LangChain
provided modular infrastructure for building agentic pipelines around LLMs
One of the first academic approaches in this area was the ReAct framework (35), where agent reasoning
choices are interleaved with action selection in order to interact with external environments. Another
notable contribution was ExpeL (38), where an agent that learns from experiences and natural language
to make informed decisions without requiring parametric updates.
Although there are many variations of this framework, for the purpose of this paper, we will use a
framework similar to the one used by Reflexion (Fig. 2 in (23)). The Reflexion agent employs an LLM
(denoted as the agent) and an environment that processes actions across multiple iterations. At each
iteration, the agent receives an observation from the environment. This observation is combined with a
prompt given to the LLM to output some action. The environment processes this action and then returns
the observation for the next iteration.
Perhaps the closest to this paper is the concurrent work of Belcak and Molchanov (3). In their universal
deep research (UDR) framework, a strategy compiler is used to take a research strategy from the user
and compile it into a list of steps and corresponding outputs that a deep research tool needs to execute
step by step. The structure is enforced by incorporating code comments and yield directives that specify
the goal of each step and the intended outputs of the step. Our approach is more general, and we
can hypothesize that there exists a task network that when applied to our system would replicate the
behavior of UDR.
LLMs and Tool-use. To supplement capabilities in domains where LLMs have poor performance, it is
common to allow LLMs to interface with external tools. These tools enhance the LLMs with capabilities
that they might otherwise not have (31) and there are numerous papers covering various aspects of this
field of research (12; 20). Early demonstrations included Toolformer ( 21), which fine-tuned LLMs to
invoke APIs from demonstrations, and MRKL (15), which integrated symbolic reasoning with tool-use.
Unlike past work, our system allows the LLM agent to write arbitrary code to call arbitrary APIs. This is
different from works where the external tools are presented in a standardized in-context format to an
LLM for usage (e.g., MCP servers). Allowing the LLM to write arbitrary code also gives more flexibility
in problem solving (e.g., coding allows the LLM to embed tool calls in algorithms), which standardized
tool formats do not permit.
Multi-agent Systems. The extension from single-agent to multi-agent frameworks has become an
important line of research. In AgentOrchestra (37), an orchestrator agent creates a plan that is then
executed by specialized sub-agents. Unlike our explicit task network representation, AgentOrchestra
uses a simple list structure. SagaLLM (4) proposes a transactional system to handle multi-step planning
in multi-agent LLM systems. Other works, such as CAMEL (19), demonstrated emergent coordination
between specialized LLM agents by role-playing tasks and negotiating via natural language.
Hybrid Systems. Various hybrid systems have been developed for application to specific domains.
For example, (11) provides a survey of LLM-based agentic recommenders that incorporate subsystems
similar to planning and acting modules. AutoConcierge ( 36) employs LLMs to convert user requests
into formalized representations to be used by a reasoner. This is also similar to the approach from (10),
where user requests and API calls are translated into constraints for an SMT solver. Both approaches
use LLMs to convert user data into formalized problem descriptions, which are then solved to provide a
solution. This is different from our approach, which instead uses a formalized representation to assist
the LLM in the problem-solving process.
Other than agentic LLM systems, there are many LLM-modulo systems that combine LLMs with external
verifiers and or solvers (14). ISR-LLM (39) employs an LLM to translate planning problems in natural
language into PDDL and then iteratively calls the external planner to verify LLM-generated plans.
Beyond agentic LLM systems, many hybrid approaches combine LLMs with external verifiers or solvers
(14). ISR-LLM (39), for instance, employs an LLM to translate planning problems in natural language
into PDDL and then iteratively calls an external planner to verify and refine plans. Similarly, program
synthesis approaches (5) use LLMs to generate candidate code that is executed and verified externally.
3
