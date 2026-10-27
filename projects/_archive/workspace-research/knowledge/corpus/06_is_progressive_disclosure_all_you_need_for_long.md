---
type: Concept
id: 06_is_progressive_disclosure_all_you_need_for_long
title: "Is Progressive Disclosure All You Need for Long-Context Agents? (part 7/17)"
source: "Is Progressive Disclosure All You Need for Long-Context Agents"
tags: [agentic, agents, anti-leakage, context-engineering, icm, memory, planning, prompt-engineering, reflection, progressive-disclosure]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

emits a scalar reward for every rollout, not only a
corpus-level accuracy: closed-form questions score
by normalized match and open questions by the
∞Bench open-QA metric, so each run carries its
own per-trajectory reward. Here we use that re-
ward only to compare disclosure conditions. But
because the environment is sandboxed and the ver-
ifier reads only the agent’s final answer, the same
per-trajectory signal could post-train an agent, im-
proving long-context reasoning with LOONGDOC
as the environment.
Navigation at library scale.We push context
length further by staging many books in one envi-
ronment for the agent to search and read. A single
question still targets one book, so a larger bun-
dle tests whether the agent can locate the answer-
bearing book before reasoning over it. A task
stages K books and asks about all of them. Moving
from K=1 to K=20 changes only how many files
we write, not the interface the agent sees, and Sec-
tion 5.2 tests the agent’s library-level navigation.
5 Results
5.1 Single-book question answering
We evaluate the three approaches over single
∞Bench (Zhang et al., 2024a) books across three
harnesses, three models, and ahybrid-rag base-
line (Appendix B.1). We report the results in Ta-
ble 1 and read two contrasts across its cells.
Disclosure helps where native navigation is
weak.The raw vs. flat contrast isolates
the disclosure mechanism itself. On Pi and
Claude-Code, the flat skill pack matches or
exceeds raw in every cell, the sole exception
being qwen3.6-27b on Zh.QA, where the
two sit within one standard deviation, and the
claude-haiku-4.5 En.MC gain clears the
high raw variance. On these harnesses a single
level of description-gated, in-skill-indexed chunk
loading already beats letting the agent navigate the
raw document on its own.
The gain is harness-dependent.The Codex
harness inverts this picture: on gpt-5.4-mini
the three approaches tie within error on all three
subsets, so the skill pack that wins under Pi adds
nothing here. Trajectory inspection explains the
gap: under raw the bare Codex agent does not
read the book linearly but builds its own retrieval,
grepping the raw text for the entities named in each
question and reading only the matched passages. It
reconstructs on the fly the locate-then-read capabil-
ity that the skill pack pre-builds, so disclosure is
redundant when the agent already navigates well
natively; for such agents a pre-cut skill buys con-
trollability of the retrieval path, not accuracy.
The gain is not reducible to retrieval.The
hybrid-rag baseline tests whether the dis-
closure gain is just retrieval in disguise. On
qwen3.6-27b it trails both raw and flat
across all three subsets, with the open-QA gap the
widest, and on gpt-5.4-mini it trails flat on
En.MC as well. Routing to a chunk through an
in-skill index thus outscores the classical rerank-
and-feed pipeline in nearly every cell.
Depth does not pay, and can hurt.The
flat vs. hierarchical contrast isolates the
value of pushing disclosure one level deeper, pro-
moting the per-chunk index out of the activated
parent body into always-loaded child-skill de-
scriptions with a meta-router on top. No cell
rewards the extra depth: hierarchical ties
flat within noise on claude-haiku-4.5 and
on Codex gpt-5.4-mini, and trails it every-
where else. On Pi it is actively harmful, collaps-
ing En.MC from 0.9126 under flat to 0.6398 on
gpt-5.4-mini and falling below flat across
all three subsets on qwen3.6-27b, steepest on
Zh.QA (0.7479 to 0.3890); each drop lands far out-
side the cells’ variance, as the always-loaded child
descriptions saturate the router’s context before it
commits to a chunk.
Takeaway.On a single book, disclosure is a
harness-dependent context-scaling tool, not a uni-
versal accuracy lever: it lifts weak-navigator har-
nesses (Pi, Claude-Code) and adds nothing to
Codex, whose bare agent already reconstructs
locate-then-read retrieval. Depth never helps on
a single book and sometimes hurts, so one flat,
in-skill-indexed level is the default; only at library
scale, on weak-navigator open-QA cells, does the
extra level recover (Section C.1).
5.2 Scaling from one book to a library
Single-book QA hands the agent the one docu-
ment a question is about; a library-scale deploy-
ment instead asks it to first find the right book
among many, then answer. We probe this with
the corpus-scale knob of Section 4: each multi-
book bundle stages K books and poses questions
about all of them, each answerable from a sin-
gle book, for K∈ {5,10,20} (Table 2). We run
6
