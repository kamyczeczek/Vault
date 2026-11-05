---
type: Concept
id: 104_icm_knowledge_big
title: "ICM_knowledge.md (part 105/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

The spec is where your creative thinking lives. What is the thesis of the video? What is the arc? What are the moments that need to land? What should feel fast and what should feel slow?

A loose spec means Claude makes more interpretive choices. It guesses more. A tight spec means you are directing at every beat. You can work either way depending on where you want your creative energy to go, but the tighter the spec, the closer the output is to what you had in mind.

------

What a spec file actually looks like

It is a markdown file. Headings for each scene. Descriptions of what happens. Notes on timing and emphasis. Nothing fancy. But it is the document that makes everything else possible.

And this is not just for creative work. This same approach works for code, for client deliverables, for anything you are building with an AI agent. The spec is always the leverage point. You will start to notice how powerful this process is across everything you do.

------

How Claude Code reads everything

Once you have a spec, the build phase is where it becomes animation. Here is what actually happens.

Claude Code reads the spec. But it also reads your documentation, because the spec references other files:

A style guide

— defines your visual language. Minimal text rules, color palettes, animation timing. Decisions that stay the same across every video.

A component registry

— a list of reusable pieces you have already built. Text animations, backgrounds, transitions, data visualizations. Building blocks that work together.

Then Claude builds each scene one by one. Each scene is a React component. Remotion takes those React components and renders them frame by frame into video.

This is the component library concept from

Section 2.5

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=190cdff0f6ed40d8b479ea675e37509a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

. You are not building from scratch every time. You are assembling existing pieces according to a spec. Claude knows the components. It knows the style rules. It composes them into scenes that match what you described.

------

Why Remotion changes the game

Remotion was created by Jonny Burger. The core insight: a video is just a function of images over time. If you change the content every frame, you get animation. React is already good at describing what should appear based on some state. Normally that state is user input. In Remotion, the state is the current frame number.

You tell React what frame 47 should look like. It renders it. Do that for every frame. You now have a video.
