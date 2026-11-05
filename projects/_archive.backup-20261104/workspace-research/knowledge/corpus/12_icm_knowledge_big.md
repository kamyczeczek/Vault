---
type: Concept
id: 12_icm_knowledge_big
title: "ICM_knowledge.md (part 13/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

This course is an ongoing build. As I finish more sections of the front-end project, new lessons will appear here.

[LINK TO future lessons when available]

------

Jake's content\Building Your Stack\2.1 Why Remote Access.md

What You'll Get From This

A clear understanding of what Remote Control enables and whether you actually need it.

------

[VIDEO: Coming Soon]

------

The Feature

Claude Code now has Remote Control built in.

Start a session at your desk. Scan a QR code. Continue from your phone. Your local environment stays local. Your files, your MCP servers, your workspace. Nothing moves to the cloud. You're just accessing the session from somewhere else.

This used to require workarounds. SSH tunnels. Web interfaces. Custom front-ends. Now it's one command and a QR code.

------

What This Enables

Async workflows

Kick off a long build. Close your laptop lid. Go to dinner. Check your phone. See where Claude is. Send a quick adjustment. Put the phone away.

The work continues without you watching it. You check in when it matters.

Mobile monitoring

Some builds take time. Renders. Large code generation. Multi-step pipelines.

You don't need to sit and watch. Glance at your phone, see progress, intervene if something goes wrong.

Quick interventions from anywhere

Claude hits a decision point. It asks a question. You're not at your desk.

With Remote Control, you see the question on your phone. You answer. Claude continues. You didn't have to wait until you got home.

Voice input on mobile

Phone keyboards are slow. But phones have voice input.

You can talk to Claude. Describe what you want. Send it as a message. This changes how you interact when you're mobile.

------

What Stays Local

This is important: Remote Control is not cloud computing.

Your session runs on your machine. Your files stay on your machine. Your MCP servers, your project configuration, your

http://claude.md/

. All local.

The mobile app and web interface are just windows into your local session. Commands you send get routed to your machine. Results get streamed back. But execution happens locally.

This matters because your local setup is irreplaceable. The cloud version of Claude Code starts fresh every time. Remote Control keeps everything.

------

When to Use It

#### Good use cases:

Long builds you want to monitor without sitting at your desk

Quick approvals and decisions when you're away

Checking status from your phone while doing something else

Voice-driven instructions when typing is inconvenient

#### Not necessary for:

Short tasks you'll finish before leaving your desk

Work that requires deep focus and full screen context

Anything where you'll be back at your computer in a few minutes

Remote Control is about mobility, not about replacing desk work. If you're doing something complex that needs your full attention, stay at your desk.

------

Current Limitations

#### Remote Control is relatively new. Some rough edges:

One session at a time
