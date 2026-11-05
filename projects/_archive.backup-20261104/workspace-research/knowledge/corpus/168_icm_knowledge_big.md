---
type: Concept
id: 168_icm_knowledge_big
title: "ICM_knowledge.md (part 169/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Escape: stop safely; double escape to jump back in history

to resume sessions

Ctrl+R: show full context window output

Claude Code SDK

flag: CLI SDK (prompt, allowed tools, output format JSON/streaming)

Unix utility style: pipe in/out (git status, logs, Sentry, GCP)

Use cases: CI, incident response, pipelines

Running Multiple Sessions (Power Users)

SSH, tmux tunnels into sessions

Multiple checkouts or git worktrees for isolation

Run many sessions in parallel

Q&A Highlights

Hardest implementation part: making bash safe (static analysis, tiered permissions)

Multimodal: drag/drop images, file paths, paste; generate UI from mocks

Why CLI not IDE: universal compatibility, anticipating models making IDEs obsolete

ML/modeling usage: notebook tool, 80% of technical staff daily

------

Uncategorized\Your AI expert council is probably making worse decisions than a single prompt.md

Everyone's stacking AI experts into "councils" right now. Here's what nobody

mentions: most of them produce blander advice than a single good prompt.

I've been building multi-agent systems for a while, and the council pattern is

seductive. Load six marketing legends, let them debate, synthesize the genius.

#### Three things I learned the hard way:

Councils regress to the mean. Put Cialdini, Godin, and Vaynerchuk in a room and

"synthesize" their answers and you get generic marketing advice wearing three

nametags. The fix isn't a better synthesizer. Stop resolving the disagreement.

Let the tension stand and make one agent own the call.

The debate is where your budget dies. Distilling a book into a tight skill file

is cheap. Having agents argue in real time is not. If "minimal tokens" is your

pitch, the preprocessing is doing the work and the roundtable is the luxury.

It doesn't make the model smarter. Cold Claude already does a soft version of

all of this. What the structure buys you is named, sharp, predictable behavior.

Say that honestly — the moment you claim it makes the AI "smarter," you've oversold

None of this means don't build councils. It means build them with your eyes open.

The real test for any council: do your experts actually disagree, or do they just

agree in different vocabulary? If it's the second, you built one expert and gave

it six hats.

(Riffing off the systems thread from @Curtis Hays that @David Vogel highlighted for us and the 'systems' build — good work worth pressure-testing.)

------

Uncategorized\ai_habit__that_saved_most_time.md

#### The core habit:

decompose before you execute
