---
type: Concept
id: 07_is_progressive_disclosure_all_you_need_for_long
title: "Is Progressive Disclosure All You Need for Long-Context Agents? (part 8/17)"
source: "Is Progressive Disclosure All You Need for Long-Context Agents"
tags: [agentic, agents, anti-leakage, context-engineering, icm, memory, planning, prompt-engineering, reflection, progressive-disclosure]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Table 1: Single-book ∞Bench accuracy across agent harnesses, models, and skill-pack configurations. Cells give
mean accuracy ± standard deviation across three seeds.Boldmarks the best method within each (harness, model)
block; when the top two methods differ by less than a standard deviation we bold both as a tie. Underline marks the
best score in each task column across all settings.
Harness Model MethodEn.MC En.QA Zh.QA
Codexgpt-5.4-mini
raw 0.8943±0.0174 0.7412±0.0219 0.8652±0.0220
flat 0.8977±0.0177 0.7516±0.0210 0.8390±0.0238
hierarchical 0.8874±0.0139 0.7377±0.0242 0.8525±0.0237
Pi
gpt-5.4-mini
raw 0.8851±0.0053 0.7161±0.0329 0.6856±0.0163
flat 0.9126±0.0208 0.7259±0.0062 0.7007±0.0331
hierarchical 0.6398±0.0043 0.5120±0.0060 0.6510±0.0390
hybrid-rag 0.7628±0.0066 0.6214±0.0091 0.7020±0.0136
qwen3.6-27b
raw 0.7865±0.0355 0.6813±0.0644 0.7563±0.0177
flat 0.8023±0.0799 0.6913±0.0180 0.7479±0.0287
hierarchical 0.6460±0.0696 0.5933±0.0040 0.3890±0.1388
hybrid-rag 0.7470±0.0086 0.5439±0.0000 0.5856±0.0038
Claude-Codeclaude-haiku-4.5
raw 0.7448±0.1166 0.6892±0.0305 0.8142±0.0077
flat 0.8667±0.0170 0.7173±0.0086 0.8330±0.0062
hierarchical 0.8687±0.0267 0.7255±0.0101 0.8295±0.0133
102 103
cost per trial (cents, log; uncached UB)
30
40
50
60
70
80en.MC accuracy (%)
corpus size
K=5
K=10
K=20
corpus size
K=5
K=10
K=20
Codex·rawdoc
Codex·flat
Haiku·flat
Pi·flat
Codex·flat
Codex·hier
Pi·flat
Codex·flat
Pi·flat
Pi·hier
rawdoc (no skills) flat (skills) hier (skills)
Figure 4: Corpus-scaling cost–accuracy Pareto frontier
onEn.MC.
Codex on gpt-5.4-mini and Claude-Code on
claude-haiku-4.5 across En.MC, En.QA,
and Zh.QA; the weaker Pi harness supplies a fur-
ther En.MC contrast (Section C.1). We center
Codex deliberately: it is the harness where disclo-
sure bought nothing on single-book QA (Table 1),
so if a skill pack earns its keep here, corpus scale
breaks native navigation. In Figure 4 we place these
runs on a cost–accuracy plane (per-question cost
from real token usage); we draw En.MC here and
its En.QA companion, which carries the sharpest
disclosure effect, in Figure 9, reading Zh.QA from
Table 2. As K grows the frontier recedes down
and to the right: accuracy fallsandthe cost of
buying any fixed accuracy rises, so a larger cor-
pus is strictly less efficient, not merely harder. Its
top point also shifts from Codex raw at K=5 to
Codex flat at K≥10, so the skill pack takes over
the frontier only once the corpus is large; Codex
holds the high-accuracy end, Pi the low-cost end
at roughly 10× fewer tokens, and Claude-Code is
largely Pareto-dominated atK=20.
Corpus scale breaks the bare agent that single-
book QA did not.Even Codex loses accuracy as
K grows, and the loss is steepest on the open-QA
subsets, where questions cannot be answered from
parametric memory of a canonical novel. Under
raw, En.QA more than halves and Zh.QA col-
lapses to near zero from K=5 to K=20: the same
bare agent that matched the skill pack on a single
book cannot reliably find the target book once the
corpus grows to twenty. En.MC degrades more
gently, reflecting the pre-training confound below.
Disclosure rescues scaling where it was redun-
dant single-book.The flat skill pack de-
grades more slowly than raw, and the two di-
verge as K grows. At K=5, where the whole
corpus still fits comfortably in context, flat car-
ries a small routing overhead and trails raw on
En.MC; by K=20 it leads on all three subsets. The
En.QAK=20 gap clears one standard error (0.462
vs. 0.257) and the En.MC gap is borderline; only
Zh.QA stays directional at this sample size. The
mechanism is the corpus-routing analogue of the
single-book story: a pre-cut skill index lets the
agent commit to the target book before it burns
context traversing the library, exactly the failure
mode that sinksrawat largeK.
The rescue depends on routing depth, not on
disclosure alone.The rescue is specific to
the flat pack; hierarchical does not re-
produce it. On En.MC the two disclosure packs
7
