---
type: Concept
id: 113_icm_knowledge_big
title: "ICM_knowledge.md (part 114/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

The number enters the scoring logic. Psychometric instruments have specific scoring keys developed and validated over years of clinical research. Some items are reverse-scored (a response of 5 gets recorded as a 1, because the question was phrased in the negative direction). Subscales are calculated by aggregating specific items. This is validated, peer-reviewed arithmetic.

From there, reliability testing. Cronbach's alpha for internal consistency. Test-retest correlation for temporal stability. Statistical methods implemented in libraries like SciPy and NumPy that predate large language models by decades. The math has not changed since these instruments were validated on human populations.

------

The real ratio

#### Here is what the Ethics Engine actually looks like when you lay it out:

~10% AI calls

— sending prompts, receiving text. This is the only part that involves a language model.

~30% orchestration

— async coordination, rate limiting, retry logic, queue management.

~60% data processing

— sending and collecting prompts, managing personas, parsing, scoring, analysis, reliability calculations.

This ratio is not unique to the Ethics Engine. It shows up in every well-built AI system. The bad ones ignore it. If you were in

Section 2.5

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=190cdff0f6ed40d8b479ea675e37509a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

, you saw the same pattern: Moltbot is roughly 60/30/10 with the AI pushed entirely external. This is the 60/30/10 framework applied to research software instead of a messaging platform. Same ratio. Same architecture. Different domain.

------

Everything connects

If you have been following this series, the connections are surfacing now.

Section 2.2

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=18fb23fa6b084725937e8d47606f376a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

, we traced a line of Python down through seven layers of abstraction to electrons that are fundamentally probabilistic. In

Section 2.3

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=0964ed75790a415b909838050ecad3ea&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

, we traced memory from registers and cache through to context windows and system prompts, and found that the template pattern (blanks filled according to rules) holds at every level. In

Section 2.4

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=d8d7d437b5c74dc4a026d1dbadbeeba2&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

, we saw what happens when people build at the wrong layer. In

Section 2.5

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=190cdff0f6ed40d8b479ea675e37509a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03
