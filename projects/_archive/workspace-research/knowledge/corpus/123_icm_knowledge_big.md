---
type: Concept
id: 123_icm_knowledge_big
title: "ICM_knowledge.md (part 124/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

------

Jake's content\The Foundation\3.2 Customizing for Your Use Case.md

3.2 Customizing for Your Use Case

What You'll Get From This

You will see how the three-layer folder architecture changes shape for three different kinds of work. The layers stay the same. The names, the context files, and the routing all change. You will walk away knowing how to build yours.

------

One structure, every use case

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

you saw the full architecture: a top-level identity file (CLAUDE.md), workspace-level context files, and skills or tools that plug in where needed. The example in the video used a fake project with a community workspace, a production workspace, and a writing room.

That example was intentional. It is close enough to real work that you can see the logic, but generic enough that you have to make it your own. This lesson shows you how.

The principle is short: the layers do not change. The labels do. Your CLAUDE.md still sits at the top and routes everything. Each workspace still has its own context file. Skills still plug in where they are needed. But what each workspace is called, what the context files say, and what skills are wired in will look completely different depending on what you actually do.

Here are three real examples. Find the one closest to your situation, study it, then build your own.

------

Example 1: Content Creator

You make videos, write posts, manage a social presence, and probably do it mostly alone or with a very small team. Your work moves through a cycle: come up with ideas, write scripts or outlines, produce the content, publish it.

#### Your workspaces:

my-content-project/ ├── CLAUDE.md ├── script-lab/ │  ├── CONTEXT.md │  ├── ideas/ │  ├── drafts/ │  └── final/ ├── production/ │  ├── CONTEXT.md │  ├── briefs/ │  ├── specs/ │  ├── builds/ │  └── output/ └── distribution/ ├── CONTEXT.md ├── platforms/ ├── scheduling/ └── analytics/

#### What each workspace does:

— This is where thinking happens. Ideas go in. Drafts come out. The CONTEXT.md in this folder describes your voice, your audience, the kind of content you make, and the process you follow from idea to finished script. (could also reference separate MD files, if there is a lot of info in these) If you have a style guide or a list of topics you keep coming back to, that goes in here. Claude reads this context and writes in your voice from the first line.
