---
type: Concept
id: 246_icm_knowledge_big
title: "ICM_knowledge.md (part 247/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Run verification (build, tests, whatever's appropriate)

Do a final review pass yourself

Executor Prompt Template

The canonical executor prompt lives at

tools/executor_prompt.md

and is shared by both the Agent tool dispatches below and the

mmx_claude.sh

wrapper. When dispatching, substitute

{{CONTEXT}}

{{CONSTRAINTS}}

— do not re-invent the structure.

#### Via Agent tool (haiku / sonnet):

Agent({ description: "Task N: [short name]", model: "haiku", // or "sonnet" prompt: <contents of tools/executor_prompt.md with placeholders filled in> })

#### Via mmx_claude.sh (MiniMax M2.7 — default for simple/medium coding):

bash tools/mmx_claude.sh
 --cwd \ --task "Task N: …full task description with file paths…" \ \[--context-file ctx.md\] \[--constraints-file constraints.md\]

The wrapper reads

executor_prompt.md

, substitutes placeholders, and invokes headless

routed to M2.7. Parse the structured status line from its stdout the same way you parse an Agent report.

Cost Awareness

#### The whole point of this pattern is cost efficiency:

Haiku is ~60x cheaper than Opus

for output tokens

Sonnet is ~5x cheaper than Opus

for output tokens

A 10-task plan where 8 tasks run on Haiku, 1 on Sonnet, and 1 needs your direct attention costs a fraction of doing everything on Opus

Your Opus tokens go to planning, judgment, and review — the work only Opus can do

When NOT to Use This

— if it's a 2-line edit, just do it yourself. Dispatch overhead > savings.

Deeply coupled work

— if every task depends on every other task, sequential subagents will thrash. Do it yourself or use a single Sonnet subagent for the whole thing.

Exploration/debugging

— if you don't know what's wrong yet, investigate yourself first. Dispatch executors once you have a plan.

Already in a subagent

— don't nest this pattern. If you're an executor, just do your job.

Example Flow (background-first)

User: /advisor Add password reset flow to the auth system

You (Opus): [Read auth system, understand architecture] Plan:

1. Add resetToken +     resetExpiry columns to users table      (dispatch start, minimax)
2. Create     /api/auth/forgot-password endpoint           (dispatch start,     minimax)
3. Create     /api/auth/reset-password endpoint            (dispatch start,     minimax)
4. Add email sending     utility                        (dispatch start, minimax)
5. Create reset password UI     page                      (dispatch start, minimax)

[Dispatch tasks 1 and 4 in parallel — independent, dispatch start × 2. Each call returns a worker id instantly. You keep talking to Ari.] [Ari asks an unrelated question, you answer it inline.]
