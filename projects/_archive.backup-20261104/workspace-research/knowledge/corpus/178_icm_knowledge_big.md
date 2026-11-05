---
type: Concept
id: 178_icm_knowledge_big
title: "ICM_knowledge.md (part 179/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Depth rule.

#### Go deep where it pays:

## How it went

## Any errors

are the build map

and the error log you will mine later, so they earn detail. Stay terse on

## What it was told

, because depth there just restates the prompt and the diff, which the

commit already holds. "A lot of depth" and "do not tax every job" are both satisfied this way:

the job writes a lot only about the part that is worth a lot.

Model/effort rule.

in the frontmatter with what actually ran the

job, not what the work order's

line requested — the two can diverge (escalation,

retry, availability), and only the actual value makes the tier recoverable later.

CC_OPERATIONS.md

carries the current selectable values, not this file, so they are not duplicated here. Effort has no

meaning for models with no effort parameter (currently

claude-haiku-4-5

effort: n/a

rather than inventing one. If a job genuinely cannot tell which model or effort actually ran, write

rather than guessing.

coordination/touchdowns/pending/\_\_.md

, then committed by the job.

Before writing the touchdown, check coordination/touchdowns/pending/ and

coordination/touchdowns/completed/ for the highest four-digit sequence number present across all

files. Use the next number. If no files exist at all, start at 0001.

is a zero-padded four-digit global ever-incrementing sequence number (0001–9999), never

reset per day. Harvested by the loop (

pipeline/loop_harvest.py

) on its own cadence, independent

of priming: the verdict to

PROMPT_PERFORMANCE.md

, errors tagged

status: open

to the issues log,

map flags to

PENDING_MAP_UPDATES.md

, and each bee's Last activity to

LIVE_STATE.md

. Then moved

------

------

bee: [WOR] DC-2.x-.PC # the worker bee that spawned this job — REQUIRED slug: <task-slug> job: <n> # which job in the feature date: 2026-06-21 model: <model-id> # what actually ran this job, not what was requested — see Model/effort rule above effort: <effort-level | n/a> # what actually ran this job; n/a if the model has no effort parameter</div></body></html>

##

# CC job touchdown — #

From worker bee: [WOR] DC-2.x-.PC</div></body></html>

## Aim                 [terse — one line]

## What it was told          [terse — 2-3 sentences]

<short paraphrase of the prompt's instructions, so this record stands alone. Not the whole prompt.>

## What it did             [terse — the facts]

\-    files changed:

\-    commit: —

\-    tree: clean | dirty

\-    tests/build: green | red | n/a

## How it went             [DEEP — this feeds PROMPT_PERFORMANCE.md]

Grade: <1-5> —

## Correction passes

## Any errors             [DEEP — this feeds the issues log and the error review]
