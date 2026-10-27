---
type: Concept
id: 105_icm_knowledge_big
title: "ICM_knowledge.md (part 106/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

What this means in practice: anything that works in a web browser can be part of your animation. CSS, SVG, canvas, the entire ecosystem of JavaScript libraries. You are not learning a new tool from scratch. If you know any front-end development (or if you have Claude Code writing the front-end for you), you are using tools that have existed for years, applied to a new purpose.

------

The workflow in detail

Give Claude the spec

Point it at the documentation (style guide, component registry)

Tell it which scene to build

It writes the code

Preview it in Remotion Studio

If something is not right, describe in natural language what needs to change

Claude adjusts. Iterate until the scene matches what you had in mind.

The component library matters because you are not building every animation from scratch. You have building blocks: a text component that handles entrance animations, a scene container that handles safe margins and backgrounds, effects like glitch text or counting numbers. Claude assembles these pieces according to the spec. It is composing, not inventing.

This is separation of concerns. The same principle that makes any complex software manageable. The spec is separate from the implementation. The components are reusable. The style guide encodes decisions so you do not make them every time. Break complex things into smaller pieces that can be understood and changed independently.

If you went through

Section 1.2

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

, this should sound familiar. The folder architecture does the same thing: identity file, workspace context, skills. Each one handles a different concern. This animation pipeline is the folder architecture applied to a specific production workflow.

------

Exporting to CapCut for the final edit

Once the scenes are built, I export from Remotion (or just use OBS to record the screen, which avoids render and codec headaches). Then I bring it into CapCut.

This is where animation becomes a finished video. I record the voiceover. I cut and sync it. I add music. I scrub through and nudge transitions to land on specific words. Some of this is honestly faster by hand than describing it in a spec and waiting for code to regenerate.

The animation is not the finished video. It is a substantial starting point. I still spend real time in this phase. I cut sections that do not work when I hear them out loud. I re-record lines that do not land. I add photos, screenshots, or footage to support the narration. The animations give me a foundation. The finished video requires refinement.
