---
type: Concept
id: 58_icm_knowledge_big
title: "ICM_knowledge.md (part 59/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

In Module 2, I described a coding pyramid: machine code at the base, Python in the middle, LLMs at the top. Each layer lets a novice do what used to require an expert. I also introduced the THINK acronym for working with AI, a simple workflow for academic writing.

Both of those were early versions of the same idea. They were pointing at something I did not have a name for yet.

Now it has a name: computational orchestration.

This is the discipline of knowing which type of computation to apply to which problem. Traditional code for the deterministic parts. Language models for the semantic parts. Humans for the judgment calls. And most importantly, knowing when to use which.

The article below lays out where this idea came from, why it matters, and the 60/30/10 pattern that keeps showing up in every successful AI implementation I have built or observed. 60% traditional database queries. 30% basic rule-based logic. 10% actual AI calls, only where semantic understanding matters. The 10% makes the whole thing feel intelligent. The 90% makes it actually work.

If you came to this course through the old videos in Module 2, this is where the early thinking landed. If you started here, go back and watch those videos after reading this. You will see the seeds of everything in this article planted years earlier.

═══════════════════════════════════════

------

I've been watching something weird happen in tech, and nobody's really talking about it.

Not the AI hype - god knows we have enough of that.

I mean the thing underneath. The pattern that keeps showing up when senior engineers actually build something that works.

They're not "using AI" the way LinkedIn influencers think. Sure there is prompt engineering or now the new buzz word is “context engineering” for vibe coders.

But honestly the real developers, they're doing something else entirely. Something that doesn't have a name yet.

Well, it does now. I'm calling it

Computational Orchestration.

Here's What I Keep Seeing

Walk into any company that's actually shipping AI features (not just talking about them), and you'll find the same thing:

Some grizzled engineer who's given up trying to explain what they actually do.

I'm the AI person,

" they'll say, dead-eyed, because it's easier than explaining that they spend

80% of their time preventing AI from being used where it shouldn't be.

These people aren't prompt engineers. They're not "AI specialists." They're doing something harder - they're

orchestrating

different types of computation to

actual problems.

Traditional code for the deterministic stuff. LLMs for the semantic stuff. Humans for the judgment calls. And most importantly,

they know when to use which.

That's not a job title. That's a discipline that's emerging whether we name it or not.

Why "Orchestration" Isn't Just Another Buzzword

Look, I hate buzzwords as much as you do. Probably more. But orchestration is the only word that actually captures what's happening.
