---
type: Concept
id: 241_icm_knowledge_big
title: "ICM_knowledge.md (part 242/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

~/dispatch/questions/.md

and exit with

Status: NEEDS_GUIDANCE

(code 2). See "Checking for questions" below.

Never dispatch with

pointing at the main checkout root.

tool refuses this. Use a worktree, subdir, or other workspace.

— Claude models (

), full Claude Code tool

access in-process,

Agent({ model: "haiku"|"sonnet", description, prompt })

Use for: truly trivial inline tasks (a 1-line rename) or when you need

the result synchronously because the next step depends on it. Prefer path

1 whenever possible — the main session context window is precious and

in-process Agent calls burn it.

Executor wrappers directly

mmx_claude.sh

haiku_claude.sh

sonnet_claude.sh

. Synchronous headless

calls. Use these when

you want to wait for a result inline, not when you want to dispatch in the

background. All three share

_claude_exec.sh

as their body.

bash tools/mmx_claude.sh --cwd --task ""

#### Exit codes:

DONE / DONE_WITH_CONCERNS,

NEEDS_GUIDANCE,

claude-side failure,

wrapper error.

#### Why M2.7 is default among the three:

benchmarks (GDPval-AA 1495,

MLE-Bench-Lite 66.6%, SWE-Pro 56.22%) put it Sonnet-adjacent. Haiku is

reserved for trivial renames / format fixes. Sonnet is reserved for

judgment-heavy coding that M2.7 escalated.

— any provider, text-in/text-out, no file access.

python3 tools/ask.py -m "prompt"

Use for: non-code text, research, second opinions, video (gemini), bulk

generation (gemma), long-context docs (kimi).

Parallel dispatch example (all four paths in one message block)

[Bash("python3 tools/dispatch.py start
 --executor minimax
 --task-file /tmp/task-1.md
 --cwd .claude/worktrees/feat-x
 --label impl-foo")]                           # path 1 (default) [Agent(model="haiku", description="rename foo→bar", prompt="Rename foo → bar in src/util.ts, no other changes")]       # path 2 (inline, rare) [Bash("bash tools/mmx_claude.sh
 --cwd .claude/worktrees/feat-y
 --task 'Implement /api/bar endpoint per spec.md'")]           # path 3 (synchronous) [Bash("python3 tools/dispatch.py start
 --executor opus
 --thinking max
 --task-file /tmp/task-arch.md
 --cwd .claude/worktrees/feat-z
 --label arch-review")]                          # path 1, opus, max thinking [Bash("python3 tools/ask.py -m kimi-swarm
 'Research OFX plugin distribution landscape'")]             # path 4

Path 1 returns a worker id and exits in <1s; the main session moves on. The

worker's final output lands in a log file under

~/dispatch/logs/

. Next turn, call

dispatch.py questions

to surface anything blocked on Ari.

Model Selection Rules

Coding Tasks

Trivial (1-line edits, rename, format)

Agent tool OR

dispatch.py start --executor haiku

Cheap, fast, sync or async

Simple → medium (1-3 files, clear spec)

dispatch.py start --executor minimax

Default background executor — Sonnet-adjacent brain, fraction of the cost

Complex (multi-file, refactor)

dispatch.py start --executor minimax
