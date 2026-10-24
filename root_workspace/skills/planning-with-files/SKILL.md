---
name: planning-with-files
description: "Manus-style persistent file-based planning for AI coding agents: keeps task_plan.md, findings.md, and progress.md on disk so work survives context loss and /clear. Use when asked to plan out, break down, or organize a multi-step project, research task, or any work requiring 5+ tool calls."
disable-model-invocation: true
---

# Planning with Files

Work like Manus: Use persistent markdown files as your "working memory on disk" to survive context loss and `/clear`.

## Where Planning Files Live
- Create `task_plan.md`, `findings.md`, and `progress.md` in your project root.

## Core Rules
1. **Create Plan First:** Never start a complex multi-step task without `task_plan.md`.
2. **The 2-Action Rule:** After every 2 view/browser/search operations, immediately save key findings to text files (`findings.md`).
3. **Read Before Decide:** Before major decisions or new phases, re-read planning files to keep goals in context.
4. **Update After Act:** Mark completed phases in `task_plan.md`, log errors, and record steps in `progress.md`.
5. **Log All Errors & Never Repeat Failures:** Track errors and mutate your approach; never repeat a failing action.

## Templates
- **`task_plan.md`**: Phases, progress, and decisions.
- **`findings.md`**: Research and discoveries.
- **`progress.md`**: Session log and execution trail.
