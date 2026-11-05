---
type: Concept
id: 14_icm_knowledge_big
title: "ICM_knowledge.md (part 15/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fd76648c16ad429fb6e828b01bfa9177&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

#### Build a custom UI on top of this:

Module 1: Custom UI for Claude

https://www.skool.com/quantum-quill-lyceum-1116/classroom/2a86a1d1?md=c7a59d0fa0c145549dc9126470b7f82f&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

------

The why is clear. Now let's get it running. One command, one QR code, and you're connected.

------

Jake's content\Building Your Stack\2.2 Setting Up Remote Sessions.md

What You'll Get From This

Remote Control running and connected to your phone.

------

[VIDEO: Coming Soon]

------

Three Ways to Start

You have three options depending on where you are in your workflow.

Option 1: Server Mode

Start a session that's remote-only. Your terminal shows connection status but you interact from your phone or browser.

claude remote-control

#### Or the short version:

Your terminal displays a session URL and a QR code. Press spacebar to toggle the QR code display.

Option 2: Interactive + Remote

Start a normal session that's also accessible remotely. You can type in your terminal AND control from your phone. Both stay in sync.

claude --remote-control

claude --rc

This gives you the full terminal experience with remote access layered on top.

Option 3: Enable Mid-Session

Already in a Claude Code session and want to continue it remotely? Use the slash command:

/remote-control

This starts Remote Control on your existing session. Your conversation history carries over. You get a session URL and QR code.

------

Connecting From Your Phone

#### Once Remote Control is active, you have options:

Scan the QR code

Open your phone's camera (or the Claude app). Scan the code shown in your terminal. You're in.

Use the session URL

Copy the URL from your terminal. Open it in any browser. It takes you directly to your session on

claude.ai/code

http://claude.ai/code

Find it in the app

claude.ai/code

http://claude.ai/code

or the Claude mobile app. Your Remote Control session appears in the session list with a computer icon and green status dot.

------

What You See

#### In your terminal:

Connection status. Whether someone's connected. Tool activity as Claude runs commands. It's a dashboard of what's happening.

#### On your phone/browser:

The same conversation. The same context. You can send messages, see Claude's responses, approve actions. Everything stays synchronized.

If you send a message from your phone, it appears in the terminal. If Claude runs a command locally, you see the result on your phone.

------

The Workflow

#### Here's how a typical session goes:

Start at your desk.

You're in your project folder. You kick off a task.

claude --rc

Work normally.

Type in your terminal. Get Claude going on something.

Grab lunch. Run an errand. The session keeps running.

Check your phone.
