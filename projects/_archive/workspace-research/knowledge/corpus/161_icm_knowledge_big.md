---
type: Concept
id: 161_icm_knowledge_big
title: "ICM_knowledge.md (part 162/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

examples — Matched do / don't pairs of real input → output, each annotated with why. (See below — this is the highest-leverage file in the folder.)

#### Two more rules that separate good specialists from generic ones:

Scope lists earn trust through specificity. "I don't do SEO" is vague. "I don't do semicolons — get a linter" is opinionated enough to be believed. The more concrete the exclusion, the more credible the inclusions.

Define the clean-pass output explicitly. A specialist with no defined "nothing wrong here" result will invent noise to look useful. Give it a contractual silence: PASS — 0 issues, STRONG — 92/100, No changes recommended.

#### Why examples carry the most weight:

Of the five files, examples is the one most people underbuild and the one that moves quality the most. Here's why, and how to build it well.

#### Why it works:

Examples encode the tacit knowledge that rules can't. A rule can say "be specific," but it cannot fully transmit what specific looks like in this domain. One concrete good-output makes the standard legible in a way ten adjectives never will. The rule names the target; the example is the target.

Models pattern-match harder off examples than off instructions. When an AI sees a worked input→output pair, it anchors to the shape, depth, and tone of that output. A single strong example pins down a whole class of decisions that would otherwise drift run-to-run — formatting, length, how much to push back, when to stop.

The "don't" half is where the boundary actually lives. A good-only example shows the destination but not the edge. A bad example — especially a near-miss that looks plausible but fails — teaches the line between acceptable and not. Most specialist failures are subtle (technically-correct-but-useless output), and only a contrastive pair makes that line visible.

Annotated pairs turn examples into a rubric. When each example says why it's good or bad, the specialist isn't just imitating a sample — it's internalizing the criterion. That's what lets it generalize to inputs you never showed it.

#### How to build it well:

Use matched do/don't pairs, not isolated samples. Same input, two outputs: one that passes, one that fails. The contrast is the lesson.

Annotate every example with the reason. One line under each: "Good — names the exact location and a reproduction step." / "Bad — flags a 'concern' with no evidence; this is the noise the clean-pass rule exists to kill."

Mine the near-misses, not the obvious failures. A bad example that's wildly wrong teaches nothing. The valuable "don't" is the one that looks right at a glance and fails on inspection — that's the mistake the specialist will actually be tempted to make.

Include the clean-pass case. Show one example where the correct output is "nothing to report." This is what stops a specialist from manufacturing problems to seem useful.
