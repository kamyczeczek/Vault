---
type: Concept
id: 242_icm_knowledge_big
title: "ICM_knowledge.md (part 243/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

First swing, escalate to Sonnet on BLOCKED

Deep reasoning / ambiguous design

dispatch.py start --executor sonnet

Judgment-heavy coding, M2.7 escalation target

Self-improvement cycles

dispatch.py start --executor opus --thinking max

Opus-only — never delegate harness-wide judgment to cheaper brains

Architecture, planning, review, surfacing

You (Opus in main session)

Never delegate judgment calls that shape the conversation

#### Dispatch paths:

dispatch.py start --executor

— default, background, invisible. Returns a worker id in <1s. Questions surface via the UserPromptSubmit hook automatically. All four wrappers (

mmx_claude.sh

haiku_claude.sh

sonnet_claude.sh

opus_claude.sh

--add-dir PATH

(repeatable) for extra read/write paths and

--read-only

for tool-list stripping (Write, Edit, MultiEdit, NotebookEdit all become

#### No such tool available

--dangerously-skip-permissions

is the default so workers don't stall on approval prompts.

Agent tool (foreground)

— synchronous, blocks main session. Keep for trivial inline tasks where async overhead > savings.

— text-only, no file access. For cheap second opinions, kimi-swarm research, gemma local inference.

Read-only review example

(won't modify any files):

dispatch.py start
 --executor sonnet
 --cwd /private/tmp/review-\ --add-dir ~/proj/tools \ --read-only \ --task-file /tmp/review-task.md

#### Code via ask.py (text-in/text-out):

Still available for

when you want a second opinion or a non-Anthropic perspective. Model returns text; you place it into files yourself. No file access, cheapest path.

Opus thinking tier

#### When dispatching

--executor opus

--thinking

to scale extended-thinking budget. Aliased onto Claude Code's native

flag. Default:

When to use

Opus chosen for context/judgment, task itself mechanical (small-diff review, format normalization)

Multi-file refactor, ambiguous bug fix, plan critique

Architecture decisions, rule-system changes, anything where being wrong propagates

Self-improvement cycles, breaking-change migrations, security-sensitive code paths

Escalation on

re-dispatch one tier higher with the previous failure context baked into the new task prompt. Sequence:

mid → high → highx → max → giveup

, take the task back into the main session or decompose it. Tier is

auto-bumped by

dispatch.py answer

— escalation is an explicit decision.

NEEDS_GUIDANCE

is not by itself a tier-escalation signal. Re-dispatch at the same tier with the answer baked in unless the failure looks reasoning-bound rather than information-bound.

Non-Code Tasks

Complex multi-step research

Extended reasoning, deep analysis

Long-context (large docs, transcripts)

Video analysis (scenes, pacing, edit review)

ask.py --video

Second opinion from different model family

Drafts, copy, captions, reformatting

Bulk generation (many items)

(Ollama, free)
