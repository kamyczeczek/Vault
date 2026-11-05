---
type: Concept
id: 08_is_progressive_disclosure_all_you_need_for_long
title: "Is Progressive Disclosure All You Need for Long-Context Agents? (part 9/17)"
source: "Is Progressive Disclosure All You Need for Long-Context Agents"
tags: [agentic, agents, anti-leakage, context-engineering, icm, memory, planning, prompt-engineering, reflection, progressive-disclosure]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Table 2: Multi-book corpus-scaling accuracy on ∞Bench. Conventions follow Table 1, except that cells give mean
±standard error across bundles and seeds rather than seed-level standard deviation.
Harness Task MethodK=5K=10K=20
Codex
gpt-5.4-mini
En.MC
raw 0.818±0.019 0.767±0.027 0.720±0.019
flat 0.752±0.034 0.790±0.021 0.760±0.014
hierarchical 0.777±0.043 0.791±0.018 0.746±0.017
En.QA
raw 0.657±0.041 0.577±0.044 0.257±0.067
flat 0.708±0.023 0.582±0.045 0.462±0.061
hierarchical 0.667±0.030 0.606±0.018 0.267±0.069
Zh.QA
raw 0.698±0.074 0.214±0.092 0.043±0.022
flat 0.738±0.056 0.178±0.079 0.095±0.043
hierarchical 0.771±0.046 0.137±0.070 0.097±0.043
Claude-Code
claude-haiku-4.5
En.MC
raw 0.745±0.024 0.653±0.016 0.459±0.047
flat 0.781±0.033 0.636±0.035 0.482±0.037
hierarchical 0.777±0.021 0.655±0.020 0.521±0.043
En.QA
raw 0.582±0.038 0.413±0.021 0.301±0.037
flat 0.642±0.023 0.480±0.025 0.354±0.045
hierarchical 0.589±0.027 0.453±0.032 0.302±0.035
Zh.QA
raw 0.730±0.025 0.550±0.027 0.499±0.069
flat 0.696±0.030 0.576±0.023 0.401±0.046
hierarchical 0.687±0.029 0.533±0.040 0.389±0.045
track each other and both clear raw at K=20,
but on open QA they part: at K=20 on En.QA,
hierarchical collapses back onto raw while
flat holds well over 1.7× their accuracy. The
mechanism follows from what each pack keeps
in context: hierarchical always loads every
chunk’s description, so a twenty-book library in-
flates the always-on budget and recreates the con-
text pressure that disclosure is meant to relieve,
whereas flat pays for a per-chunk summary only
when it reads that chunk. At library scale the flat
single-index pack is therefore the better default,
and the single-book verdict that the two are inter-
changeable does not carry over.
A second harness reproduces the En.QA res-
cue on a weaker model.The full Claude-Code
grid on claude-haiku-4.5, a weaker model
than gpt-5.4-mini, reproduces the En.QA
pro-skill signal at every scale: flat leads raw
across all three K, with the K=10 gap clearing two
standard errors, so the rescue survives a change of
both harness and model. hierarchical again
fails to reproduce it, trackingraw at every K while
flat stays ahead. The other two subsets cut the
other way. On En.MC the three configurations stay
within a standard error at every K on both grids,
the memorized-novel confound blunting any dis-
closure signal; but on the weaker Pi harness flat
leads raw on En.MC at every K (Table 3), fur-
ther evidence that the flat pack is the best default.
On Zh.QA the skill is neutral-to-negative, and at
K=20raw leads; this cell stays directional at our
sample size, and the multi-book gap tracks base-
model capability rather than the skill pack.
Takeaway.At library scale the flat skill pack be-
comes an accuracy tool even for the strong Codex
agent: it beats the bare agent in all six En.QA
cells across two harnesses and two models, the
most robust effect in the table. The payoff is task-
and language-specific, sharpest on English open
QA and absent on Chinese, where the base model,
not the skill pack, sets the ceiling.
6 Conclusion
We ran the first controlled study of progressive
disclosure for agentic long-document reasoning,
comparing raw-document navigation, flat and hi-
erarchical skill packs, and a hybrid retriever on
∞Bench across three harnesses and three model
families. Progressive disclosure buys context, not
intelligence: on a single book a strong agent al-
ready greps the passages it needs, so disclosure
adds nothing, but once the corpus outgrows what
native navigation can hold, flat disclosure becomes
decisive. A second routing level never reproduces
this gain and sometimes breaks accuracy. For pack-
aging book-length material the guidance is con-
crete: package a book as one skill layered progres-
sive disclosure, not as a multiple parallel packages
of child skills with always-loaded description.
8
