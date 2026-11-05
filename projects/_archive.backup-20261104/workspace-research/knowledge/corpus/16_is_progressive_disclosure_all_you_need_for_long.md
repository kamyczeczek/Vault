---
type: Concept
id: 16_is_progressive_disclosure_all_you_need_for_long
title: "Is Progressive Disclosure All You Need for Long-Context Agents? (part 17/17)"
source: "Is Progressive Disclosure All You Need for Long-Context Agents"
tags: [agentic, agents, anti-leakage, context-engineering, icm, memory, planning, prompt-engineering, reflection, progressive-disclosure]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Table 3: Additional multi-book corpus-scaling results for the Pi harness on gpt-5.4-mini, in the same setting
as Table 2. Cells give mean accuracy ± standard error across bundles and seeds (n=30 for En.QA and Zh.QA).
Boldmarks the best method within each (task,K) column, matching Table 2.
Task MethodK=5K=10K=20
En.MC
raw 0.410±0.054 0.391±0.048 0.333±0.052
flat 0.470±0.030 0.434±0.052 0.386±0.054
hierarchical 0.463±0.033 0.386±0.044 0.299±0.067
En.QA
raw 0.392±0.022 0.276±0.023 0.128±0.023
flat 0.432±0.036 0.221±0.037 0.184±0.038
hierarchical 0.364±0.027 0.310±0.025 0.168±0.027
Zh.QA
raw 0.510±0.024 0.414±0.031 0.287±0.045
flat 0.378±0.044 0.283±0.039 0.137±0.037
hierarchical 0.505±0.034 0.307±0.046 0.330±0.043
102 103
cost per trial (cents, log; uncached UB)
20
40
60en.QA score (%)
corpus size
K=5
K=10
K=20
corpus size
K=5
K=10
K=20
Codex·flat
Pi·rawdoc
Pi·flat
Codex·flat
Codex·hier
Haiku·flat
Pi·rawdoc
Codex·flat
Haiku·flat
Pi·rawdoc
rawdoc (no skills) flat (skills) hier (skills)
Figure 9: Corpus-scaling cost–accuracy Pareto frontier
on En.QA, the Codex-and-Claude-Code companion to
the En.MC plane of Figure 4. Axes, markers, and per-
K frontier lines follow that figure; accuracy is shown as
a percentage of theEn.QAscore.
K (Section C.3); En.QA is the subset on which
disclosure separates from bare navigation. Neither
harness is scaling-robust here the way Codex is
on En.MC: every curve recedes down and to the
right with K, because open QA cannot fall back on
parametric memory of a canonical novel, yet the
ordering at each K still favors flat. Cost sharp-
ens the verdict. At K=20raw reads the most
tokens (68.3M/question, an uncached upper bound
of $52) for the worst accuracy, the bare agent burn-
ing context re-reading the library and still misrout-
ing. flat reaches nearly double the accuracy at
roughly half the tokens and half the cost ( 32.5M,
$25): at library scale the flat pack is both the more
accurate and the cheaper choice.
C.3En.MCunder the memorized-novel
confound at scale
On En.MC the three configurations stay within a
standard error at every K under both the Codex
and Claude-Code grids, so no approach separates
cleanly. The memorized-novel confound (see Limi-
tations) blunts the comparison at the smaller scales;
only at K=20 does hierarchical edge ahead
in point estimate, a weak hint that broad traversal
of the always-loaded index helps once the corpus is
largest. We read this as directional, not as a claim.
C.4 Cost accounting for the scaling frontier
The per-question cost on the cost–accuracy plane
of Figure 4 and Figure 9 is an uncached upper
bound: it sums real per-call token usage with
no prompt caching. The always-loaded descrip-
tions that flat and hierarchical carry are
the most cache-friendly part of the input, repeated
across every question about a book, so caching
them would cut disclosure’s cost more than raw’s
and push disclosure further ahead on the frontier.
We report the uncached figure as the conservative
case.
16
