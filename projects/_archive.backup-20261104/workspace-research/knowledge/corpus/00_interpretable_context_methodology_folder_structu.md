---
type: Concept
id: 00_interpretable_context_methodology_folder_structu
title: "Interpretable Context Methodology: Folder Structure as Agent (part 1/21)"
source: "Interpretable Context Methodology Folder Structure as Agent.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, interpretable-context]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Interpretable Context Methodology: Folder Structure as Agent
Architecture
JAKE VAN CLIEF, DAVID MCDERMOTT,Eduba, University of Edinburgh, USA
Current approaches to AI agent orchestration typically involve building multi-agent frameworks that manage context passing,
memory, error handling, and step coordination through code. These frameworks work well for complex, concurrent systems.
But for sequential workflows where a human reviews output at each step, they introduce engineering overhead that the
problem does not require. This paper presents Interpretable Context Methodology (ICM), a method that replaces framework-
level orchestration with filesystem structure. Numbered folders represent stages. Plain markdown files carry the prompts
and context that tell a single AI agent what role to play at each step. Local scripts handle the mechanical work that does not
need AI at all. The result is a system where one agent, reading the right files at the right moment, does the work that would
otherwise require a multi-agent framework. This approach applies ideas from Unix pipeline design, modular decomposition,
multi-pass compilation, and literate programming to the specific problem of structuring context for AI agents. The protocol is
open source under the MIT license.1
CCS Concepts:•Human-centered computing → Interactive systems and tools;HCI design and evaluation methods;•
Computing methodologies→Artificial intelligence;•Software and its engineering→Software design engineering.
Additional Key Words and Phrases: context engineering, human-AI interaction, AI agent orchestration, filesystem architecture,
human-in-the-loop, mixed-initiative systems, workflow automation
1 Introduction
There are genuinely good agentic frameworks available today. CrewAI, LangChain, AutoGen, and others handle
multi-step orchestration, memory management, tool use, and error recovery. They work. But they work within
their own structures, and adjusting those structures requires development work. Changing the order of steps,
swapping a prompt, adding or removing a stage, skipping something that is not relevant today: these actions
typically mean editing code, understanding abstractions, and redeploying. For practitioners whose workflows are
sequential and need human review at each step, the control surface can be much simpler.
This paper describes Interpretable Context Methodology (ICM), a method for orchestrating AI agent workflows
using folder structure, markdown files, and local scripts. The central observation is straightforward: if the prompts
and context for each stage of a workflow already exist as files in a well-organized folder hierarchy, you do not
need a coordination framework to manage multiple specialized agents. You need one orchestrating agent that
reads the right files at the right moment. The folder structure tells it what to do at each step, and if the agent
delegates sub-tasks, the same folder structure determines what context those sub-agents receive. Local Python
scripts handle the parts that do not need AI: fetching data, moving files, formatting output, sending emails.
This is going backward before going forward. The principles that made Unix pipelines effective in the 1970s2
and multi-pass compilers tractable in the 1980s apply directly to AI agent orchestration in the 2020s. ICM applies
those principles to the specific challenge of structuring context for language models.
The central question this paper examines is how structuring the context delivery mechanism as a filesystem
hierarchy affects practitioners’ ability to control, inspect, and edit AI agent behavior across multi-step workflows,
and what this structure means for the quality of the model’s output at each stage.
1https://github.com/RinDig/Interpretable-Context-Methodology-ICM-
2Programs that do one thing. Output of one becomes input of another. Plain text as universal interface. These ideas are over fifty years old
and they hold up.
Author’s Contact Information: Jake Van Clief, David McDermott, theceo@eduba.io, Eduba, University of Edinburgh, Palm Coast, Florida,
USA.
arXiv:2603.16021v2  [cs.AI]  18 Mar 2026
