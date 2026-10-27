---
type: Concept
id: 98_icm_knowledge_big
title: "ICM_knowledge.md (part 99/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Same task. Clean architecture. Everything flows through one intelligent router.

------

Getting the terms straight

People use these words interchangeably. They should not.

— The actual intelligence. GPT, Claude, Llama. The thing that processes language and generates responses. OpenClaw is not this.

— A thin layer around an API. Minimal added value. Takes someone else's AI and puts a slightly different interface on it. OpenClaw is not really this either.

— An AI that can take actions on its own. OpenClaw enables this, but it needs an external AI to do it.

Orchestration layer

— Coordinates AI plus tools plus channels plus context. This is what OpenClaw actually is.

The simplest way to think about it: OpenClaw is the highway system. You still need to bring your own car. But the highway decides which routes to take, manages traffic, and gets deliveries where they need to go.

------

Inside the architecture

So what does the codebase actually look like if there is no AI model inside?

OpenClaw is built in layers. At the top, a channel layer that connects to messaging platforms: WhatsApp (using a library called Baileys), Telegram (through Grammy), Discord (through Discord.js), Signal (through Signal CLI). Each of these is a solid, maintained open-source library that knows how to speak the platform's language.

In the middle, a gateway. This is the brain of the operation, and not an AI brain. A routing brain. It is a websocket server running locally on your machine. Every message from every channel flows through here. The gateway decides where it goes. It manages sessions so the AI remembers your conversation context. It handles authentication so random people cannot message your AI.

At the bottom, two things: tools and AI models. The tools are built in (browser automation, bash commands, file operations, scheduling, webhooks). The AI models are empty hooks. You bring your own. You plug in your Anthropic API key or your OpenAI key or you run a local model through Llama and point it at OpenClaw. OpenClaw handles all the API calls. The intelligence, the actual thinking, comes from somewhere else. Somewhere you are probably already paying for.

------

The 60/30/10 breakdown

Here is where this gets practical. The OpenClaw codebase breaks down roughly like this:

is channel integrations. The code that talks to WhatsApp, Telegram, Discord, and the rest.

is the gateway. Routing logic, session management, security.

is tools. Browser control, bash execution, file handling.

is CLI configuration and AI calls. Just the code that sends messages to whatever model you configured.

This maps almost perfectly to a framework I use in all of my workshops and consulting work:
