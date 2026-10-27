---
type: Concept
id: 15_icm_knowledge_big
title: "ICM_knowledge.md (part 16/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Open the Claude app. Find your session (computer icon, green dot). See the progress.

Intervene if needed.

Claude asks a question? Answer from your phone. Need to adjust direction? Send a message.

Return to your desk.

Your terminal still shows everything. Pick up where you left off.

The conversation is the same everywhere. You're not switching between different sessions. It's one session, multiple access points.

------

Naming Your Sessions

By default, Remote Control sessions are named after your last message or "Remote Control session" if there's no history.

#### You can name them explicitly:

claude remote-control --name "animation-build"

#### Or rename an existing session:

/rename animation-build

Useful when you're running multiple projects and want to find the right session from your phone.

------

What Can You Do Remotely?

#### Everything you can do in the terminal:

Send messages and prompts

See Claude's responses

Approve file changes

Monitor tool activity

Stop and redirect

You're not limited to read-only. This is full control.

------

What Happens When You Disconnect?

#### If you close the Claude app or navigate away:

The session keeps running on your machine

Reconnect anytime and pick up where you left off

Auto-reconnect usually works if your phone briefly loses connection

#### If your laptop sleeps:

Usually fine. The session should reconnect when it wakes.

Depends on your power settings. If sleep kills the terminal process, the session ends.

#### If your terminal closes:

The session ends. You'll need to start a new one.

claude --rc

again in the same folder to start fresh.

------

Keep your terminal running

Don't close the terminal window. Minimize it if you want. But if the process exits, the remote session ends.

Check your power settings

Make sure your laptop doesn't kill terminal processes when the lid closes or when it sleeps. "Sleep" is usually fine. "Hibernate" or aggressive power saving can kill the session.

Use named sessions

If you work on multiple projects, name your sessions. Makes them easy to find from your phone.

Start remote-enabled from the beginning

If there's any chance you'll want to step away, use

claude --rc

instead of just

. Easier than remembering to run

------

Troubleshooting

"I can't find my session in the app"

Make sure Remote Control is actually running. Check your terminal for the session URL. If the process died, the session is gone.

"Messages aren't syncing"

Check your network connection on both devices. If one side is offline, sync will resume when it reconnects.

"I'm getting API errors"

This happens occasionally. The feature is still being refined. Usually restarting the session fixes it:

# In terminal, exit and restart

claude --rc

"The session died while I was away"

Your terminal process likely exited. Check if your laptop hibernated or if something closed the terminal. Start a new session.

------

Command Reference
