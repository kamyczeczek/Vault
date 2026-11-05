---
type: Concept
id: 110_icm_knowledge_big
title: "ICM_knowledge.md (part 111/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

------

Jake's content\The Foundation\2.7 From Nazi Psychology to AI Auditing.md

2.7 From Nazi Psychology to AI Auditing

#### Full paper:

[2510.11742] The Ethics Engine: A Modular Pipeline for Accessible Psychometric Assessment of Large Language Models

https://arxiv.org/abs/2510.11742

What You'll Get From This

You will see a real AI system taken apart piece by piece. What you find inside is not magic. It is APIs, async programming, parsing, and statistics. The AI is 10% of the system. The other 90% is engineering that has existed for decades. This is the final lesson in the series (for now) and it ties everything together.

------

The written version below covers the same ground as the video. The video above has music and visuals that make the layering easier to follow. The written version is the one you hand to Claude or come back to for reference.

------

A test designed to study authoritarians, now running on AI

I took psychometric tests originally used to measure authoritarian tendencies in the 1950s and aimed them at AI models. But I did more than that. I built a data pipeline that can administer a wide range of personality tests across multiple AI models simultaneously. It can tell you where a model lands on moral foundations, authoritarianism scales, personality dimensions. It can do this across personas, model variations, and different providers.

From the outside, it looks like one intelligence studying another. Something that would require a team of researchers or grants. But I am not bringing this up to show you the results. I want to take it apart. Because something becomes visible when you deconstruct systems that stays hidden when you only watch them get assembled.

------

What "agent" actually means

Before we open the system, we need to deal with a word that has taken on a lot of weight: agent.

We hear about AI agents that browse the web, write code, manage calendars, analyze documents. The word implies autonomy. Decision-making. Something that can act on its own behalf.

But language is running ahead of the engineering. What we call an AI agent in the vast majority of cases is not a single entity making autonomous decisions. It is a collection of prompts, structured and sequenced by traditional code, that causes a model to behave differently at different stages of a workflow.

The model itself is not deciding to take the next step. The orchestration layer, which is regular software, evaluates the model's output and determines what prompt to send next based on conditions that a human engineer defined.
