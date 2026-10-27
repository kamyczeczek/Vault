---
type: Concept
id: 166_icm_knowledge_big
title: "ICM_knowledge.md (part 167/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Sessions run on remote containers – close laptop, keep working

Remote Control (Phone)

/remote-control

→ session appears in mobile app

Push notifications when input needed – respond from anywhere

Background Loops – Remove Yourself from the Loop

Recurring tasks that don’t need you

Babysitting PRs (review comments, merge conflicts, CI failures)

Updating documentation

Triaging issues / monitoring feedback

Keeping CI green

Run a prompt on a fixed interval (e.g.

/loop 10 minutes: babysit my open PRs

Session wakes up, runs prompt, acts using tools + skills

Routines (Remote Background Loops)

but running in Cloud Code on the Web

Triggers: time‑based (every morning) or event‑based (new issue)

Examples: update docs daily, post feedback to Slack every 6 hours

Verification makes Claude reliable

Multi‑Clauding scales your capacity

Background loops remove you from the hot path

→ You focus only on what truly needs your attention

------

Uncategorized\Version control for the AI age.md

Git assumes a person sits down, makes a deliberate change, and writes a commit message. That world is fading. Today an AI agent might touch fifty files while you watch, or while you don't, and the question that matters isn't "what did I commit?" It's "what just happened, who did it, and how do I undo it?"

GiTeam is version control rebuilt for that question.

Why I'm building this

I built my own IDE, TeamIDE, and then spent half my time fighting the git workflow under it. Running several projects at once with AI agents in the loop, the cracks showed: worktrees are clumsy, submodules are a nightmare, and a model that's brilliant for a solo developer becomes a hindrance the moment AI joins in. I'm comfortable at the systems level, so instead of wrestling git into a shape it resists, I built what I actually needed.

What it does

Auto-history. Every save is recorded automatically, the moment a file hits disk: an append-only stream of snapshots from every human and every agent. Always on, through a background service. No staging, no remembering to commit.

Real commits, when you want them. Deliberate, git-compatible checkpoints sit over that stream as bookmarks, and they push to GitHub like any other history.

Nothing is ever lost. The history is append-only and never rewritten. Undo isn't a destructive pop off a stack, it's moving along a timeline. Edit from a past point and it automatically forks into a tree, not a line.

Every change has an author. Human or agent, stamped on every snapshot. Turn an agent loose and you get a flight recorder: attributed, reversible, complete. The undo button for autonomous work.

A cockpit to work in. A full-screen app where your agent runs in a pane beside your file tree, your editor, and a live, scrubbable history. Watch it edit, see each change attributed, scrub back and fork when it goes wrong.
