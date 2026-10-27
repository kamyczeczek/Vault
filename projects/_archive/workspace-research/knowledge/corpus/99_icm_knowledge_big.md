---
type: Concept
id: 99_icm_knowledge_big
title: "ICM_knowledge.md (part 100/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Build AI tools with roughly 60% traditional code (platform integrations, networking, file handling, stuff that has nothing to do with AI), 30% rule-based logic (routing decisions, management, security rules, smart code that is still not AI models), and only about 10% actual AI processing

In OpenClaw's case, that 10% is even pushed externally. It is API calls to someone else's AI.

This is not a criticism. This is a recommendation on architecture. Most production AI systems look like this. The AI is a component, not the whole thing. The value is in everything around the AI, not the AI itself. OpenClaw just makes this more visible than most tools do.

------

The question nobody is asking

Here is where we need to be honest. There is a question hanging over OpenClaw that nobody seems to be asking.

What happens when the big players build this themselves?

Picture this. Next year, Anthropic announces Claude everywhere. Native integration with WhatsApp. Built into Slack. Discord bot that works out of the box. No configuration, no API keys, no self-hosting. Just Claude, everywhere.

Why would anyone need OpenClaw?

This happens constantly in tech. A platform adds a feature that makes your whole product unnecessary. Some people call it getting "Sherlocked" (after Apple's habit of building features that killed third-party apps).

But there is another way this plays out. OpenClaw is model agnostic. You can swap Claude for GPT or Llama or a local model. No vendor lock-in. OpenClaw is self-hosted. Your conversations stay on your hardware. Your data, your rules. And OpenClaw is open source. 2,000 contributors. Community-driven development. Features that matter to users, not shareholders.

So the question becomes: in a world of orchestration layers and frontier models, where does the value actually live?

------

What this teaches you

Forget OpenClaw for a second. Here is the lesson underneath it.

Every time you look at an AI tool, an AI startup, an AI framework, ask yourself three questions:

Where is the intelligence?

Is it in the product, or is the product calling someone else's AI? If you removed the AI model, what would be left?

Where is the value?

Is the value in the AI itself, or in the routing, the integrations, the architecture around it? OpenClaw has zero AI and 350,000+ stars. The value is the orchestration.

What gets commoditized next?

If Anthropic or OpenAI builds the orchestration layer natively, what happens to the product? If the AI models get cheaper, what happens to the business model? Value lives above whatever just got commoditized. Always.

This is the same pattern from

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=18fb23fa6b084725937e8d47606f376a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03
