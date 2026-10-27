---
type: Concept
id: 03_icm_knowledge_big
title: "ICM_knowledge.md (part 4/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

The research and planning phase of a custom build: finding existing repos, creating a PRD, and setting up your workspace so Claude has context from the start.

------

Where This Started

David had been making animations with Claude Code. He watched my tutorials, set up his own workflow, and started building really great stuff.

Then he asked a question: what if I built a front-end UI that lets me control and monitor Claude?

It's a natural next step. Once you're comfortable with Claude Code in VS Code, you start wanting something designed around YOUR specific workflow. Something you can observe. Something with a better interface for what you're actually doing.

The problem is how to build it without burning through API credits.

------

The API Cost Problem

When you use Claude Code through your subscription, it doesn't cost extra per message. You're using what you already pay for.

But as soon as you build a custom front-end, the obvious approach is to make Anthropic API calls directly. And API calls add up fast. A heavy build session could cost more than a month of subscription.

The solution: build a front-end that controls Claude Code, not one that replaces it. You're making a better interface for the tool you already have, not a separate app that needs its own API connection.

This is the key insight that shapes everything else.

------

Research Before Building

Before writing any code, I had Claude research what already exists.

#### There are repos out there that do versions of this:

Front-ends that wrap Claude Code

Usage tracking dashboards

Mobile interfaces for remote control

Session persistence tools

I looked at them. Some had good ideas. Some had features I'd never use. None of them matched my workflow exactly.

#### But that's fine. I'm not looking for a perfect solution. I'm looking for:

What problems have other people already solved?

What code can I borrow?

What patterns work?

Don't reinvent the wheel. Study the wheels that exist. Take what's useful. Leave what isn't.

------

What I Didn't Like About Existing Repos

The existing front-ends weren't bad. They just weren't mine.

They had features I'd never use. Provider switching. Complex settings panels. UI elements designed for someone else's workflow.

I'd rather work in VS Code with raw folders than use an interface that doesn't fit how I think. But I also knew I could build something better FOR ME by pulling the good parts from these repos and wrapping them around my existing folder structure.

That's the goal: not a generic Claude interface, but a control surface for MY animation pipeline.

------

The PRD Document

Instead of jumping into code, I had Claude create a PRD first.

PRD = Product Requirements Document

#### Here's what went into it:

The repos I'm pulling from

\-    Links to the existing projects. What stacks they use. What I liked about each one.

#### What to cut
