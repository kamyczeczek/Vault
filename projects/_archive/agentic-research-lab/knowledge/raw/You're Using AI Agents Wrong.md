---
type: Concept
title: You're Using AI Agents Wrong
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# You're Using AI Agents Wrong — Structured Notes

## Overview
- Speaker: Theo (t3.gg) — CEO/founder of multiple companies, part-time coder.
- Core claim: He lands **50+ PRs/week** despite running companies and traveling, by using AI agents in a highly optimized workflow.
- Video is a deep dive into his personal workflow, tools, prompting techniques, and infrastructure.
- Emphasis on **iteration speed**, **reducing friction**, and **derisking the merge button**.

---

## The Problem: Losing Coding Time

- As he focused on running companies, YouTube, sponsors, etc., he had less time to code.
- Missed being "in the trenches" solving hard problems.
- Saw a spike in contributions to **T3 Code** (mid-July onward): 1–3 PRs/week → 23 → 37 → 41 → 52.
- Even during travel (Defcon, bad hotel internet), he landed 52 PRs in a week.
- Contrast: "Potatoes" (another dev) lands ~1000/month, but Theo has multiple companies.
- Conclusion: A part-time coder CEO is outshipping many full-time engineers.

---

## The Solution: A New Workflow

### Step 1: New Thread
- Hotkey for new thread in T3 Code.
- Paste task.

### Step 2: Run Remotely, Not on Your Local Machine
- **Critical:** Do not run agents on your laptop/desktop that you're using for other work.
- Ideal: A dedicated **Linux box** in another room, over-spec but doesn't need to be.
- His Linux machine has all codebases and a T3 Code server.
- Select the remote box (e.g., "BB1") to execute changes.
- Machine has all harnesses, Codex, Claude available.
- Uses **worktrees** — not perfect but good enough for spinning up many.

### Step 3: Prompting with Voice-to-Text
- Uses voice-to-text (Whisper Flow) because he's often down a hand.
- Prompt structure:
  - **Context:** Issue affecting real users, not a side project.
  - **Priorities:** Simple implementation, not confusing to users.
  - **Permission to push back:** "In my opinion..." — allows model to challenge.
  - **State of knowledge:** "I'm not sure about X..." — helps model explain what you don't know.
  - **Clear ask:** "Thorough audit of Claude Code's behavior and our implementation."
  - **Permission to stop early:** "If you see a simple fix, stop and let me know ASAP."
  - **Confidence qualifier:** "Come back when you have a confident solution" — not just "write code."
- Switches to full access, bumps effort to extra high.

### Step 4: Ignore the Thread Until Done
- **Most important step.**
- Watching threads feels productive but doesn't speed them up.
- 99% of the time you won't need to intervene.
- Go do something else.

---

## Managing Multiple Threads

- Problem: Starts too many threads and gets lost.
- Solutions:
  - **Remote Linux box** can handle 40+ agents without breaking a sweat (5% CPU).
  - Mac OS is bad at parallelizing; Linux is much better.
  - Even a $600 16-thread machine handles it fine.
  - Treat Macs as 1–2 tasks; treat Linux boxes as unlimited.
- Uses **T3 Code** sidebar as a to-do list:
  - Threads with PRs linked; merging PR auto-settles thread.
  - **Settle** removes thread from sidebar when done.
  - **Snooze** temporarily hides thread (e.g., 3 hours).
  - **Link PR to thread** manually if not auto-linked.
- Model choices:
  - **GLM-53 Flash** — impressive and cheap for audits.
  - **Luna** — also cheap; used for parallel audits.
  - Runs same audit on two different models for comparison.

---

## Prompting Techniques

### Give Context and Priorities
- Mention real users affected → importance.
- State what you want: simple, not confusing.
- Use "in my opinion" to allow pushback.

### State Your Knowledge Level
- "I'm not sure about X" → model knows what to explain.
- Helps model tailor response to your understanding.

### Clear Ask + Permission to Stop Early
- "Thorough audit" = clear task.
- "If you see a simple fix, stop and let me know ASAP" → avoids endless exploration.
- "Come back when you have a confident solution" → not necessarily code.

### Simplify Complex Output
- When model's solution is hard to parse: "Give me a simpler, easy-to-digest, explain-like-I'm-five description."
- Use tokens to reduce stress and avoid tabbing out.

### Audit Assumptions Against Your History
- Ask model to audit against your own history (e.g., Claude Code behavior) to verify assumptions.
- Prevents bugs.

### Draft Comments for Contributors
- Ask model to draft a comment for a PR contributor with core insights.
- Review before posting.
- Can let model post on your behalf (e.g., "Claude Fable responding on Theo's behalf").

---

## T3 Code Features Used

- **Sidebar as inbox**: Threads = tasks. Settle when done. Snooze to defer.
- **Link PR to thread**: Auto-settle on merge.
- **Babysit skill**: Agent monitors PR, addresses automated review comments, pushes fixes, loops until approved.
- **Tailscale share dev command**: Spin up remote dev server, get URL with pairing code, test in browser.
- **Preview build label**: Add label `preview-mac` → macOS preview DMG appears in thread for testing.
- **Unsigned download access**: Made preview downloads accessible without GitHub sign-in for testing on other machines.
- **Build time optimization**: Cleaned up signing to cut macOS build time.

---

## Testing and Verification

- **Web changes**: Remote dev server via Tailscale share; test in browser.
- **iOS changes**: Use **Squim** to build remotely and install via web app link.
- **macOS desktop changes**: Preview build label → download DMG → test on vanilla MacBook.
- **File upload changes**: User data directory shared with model; model can read files.
- **Screenshots**: Rendered directly in harness; model sees pixels inline.
- **Remote testing**: Critical for confidence before merge.

---

## Safety Nets (Not Guardrails)

- Mistakes still happen; most bugs can't be caught by reading code.
- Need a way to catch mistakes before they affect all users.
- **T3 Code nightly builds**:
  - Every 3 hours (not nightly).
  - Few thousand nightly users out of 200k+ user base.
  - Immediate reports if something breaks.
  - Stable releases almost never have regressions.
- Other options:
  - Slow rollouts (1% of users, rollback on errors).
  - Formal QA team.
- **Derisk the merge button**:
  - Don't look at PR until agents have high confidence.
  - Better ways to test changes yourself.
  - Reduce friction before PR; build confidence.
  - Safety nets make it easy to hit merge and worry later.

---

## Contribution Metrics

- 50+ PRs/week while traveling and running companies.
- More than doubled throughput while on vacation.
- T3 Code repo has examples for setting up projects for multi-agent environments.

---

## Tools Mentioned

| Tool                | Purpose                                 |
| ------------------- | --------------------------------------- |
| T3 Code             | Agentic coding IDE / workflow tool      |
| Claude Code         | AI coding agent                         |
| Codex               | AI coding agent                         |
| GLM-53 Flash        | Cheap, capable model for audits         |
| Luna                | Cheap model for parallel audits         |
| Whisper Flow        | Voice-to-text for prompting             |
| Tailscale           | Remote access to Linux box              |
| Squim               | Remote iOS build and install            |
| Browserbase         | Browser for agents (sponsor)            |
| Worktrees           | Git worktrees for isolated agent runs   |
| Linux (Ubuntu)      | Preferred OS for parallel agents        |
| macOS               | Limited to 1–2 tasks at a time          |
| Nightly builds      | Safety net for catching regressions     |
| Babysit skill       | Agent loops on PR review comments       |
| Matt Grilling skill | Alternative for questioning assumptions |

---

## Key Quotes

- "If you spend all of your time sitting and watching threads, you're not being productive."
- "You need to do whatever you can to avoid those demotivating moments."
- "Use tokens to reduce stress and likelihood that you decide to go do something else."
- "Safety nets, not guardrails."
- "Derisk the merge button."
- "If you find where there is friction in your flows... all of these are opportunities to improve your project, improve your workflow, improve the tools you use to build."
- "I want you to derisk the merge button. You shouldn't even be looking at the pull request until a bunch of agents have relatively high confidence that it's ready for you to look at."
- "Most of the bugs could not have reasonably been caught by just reading code."
- "Nightly builds give us a shitload of useful information about what may have broken."

---

## Summary of Workflow

1. **New thread** → paste task.
2. **Run on remote Linux box** (not local Mac).
3. **Prompt with context, priorities, knowledge level, clear ask, permission to stop early.**
4. **Ignore thread until done.**
5. **Use multiple models/threads** for audits and parallel work.
6. **Use T3 Code sidebar** as inbox: settle, snooze, link PRs.
7. **Test changes** via remote dev server, Squim (iOS), preview builds (macOS).
8. **Use babysit skill** to handle PR review comments autonomously.
9. **Merge with confidence** because safety nets (nightly builds) catch regressions.
10. **Continuously reduce friction** in your workflow to ship more.