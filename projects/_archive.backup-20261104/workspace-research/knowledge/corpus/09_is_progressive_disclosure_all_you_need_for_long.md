---
type: Concept
id: 09_is_progressive_disclosure_all_you_need_for_long
title: "Is Progressive Disclosure All You Need for Long-Context Agents? (part 10/17)"
source: "Is Progressive Disclosure All You Need for Long-Context Agents"
tags: [agentic, agents, anti-leakage, context-engineering, icm, memory, planning, prompt-engineering, reflection, progressive-disclosure]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Limitations
Our study leaves several threats open.
Pre-training confound on En.MC.The clear-
est threat is the pre-training confound on En.MC:
the ∞Bench multiple-choice books are canonical
English novels the models have likely memorized,
so the bare agent often answers from parametric
knowledge rather than from reading, which blunts
any disclosure signal on that subset. Two traces
sharpen the worry: even at K=20 the raw agent
answers En.MC correctly in a handful of tool calls,
far too few to have read twenty books, and the
single-book Codex trajectories show the agent rec-
ognizing a renamed book as a canonical work. The
open-QA subsets, where memory helps far less,
are the cleaner test; a held-out or synthetic-book
corpus would remove the confound.
Narrow scaling axis.We sample the corpus size
only at K∈ {1,5,10,20} within a single bench-
mark family, so we bracket the point where disclo-
sure begins to pay off only coarsely, and we cannot
say whether the effect transfers to non-narrative
corpora such as code or technical manuals.
Task- and language-specific gains.The gains
are task- and language-specific rather than uni-
versal, sharpest on English open QA and ab-
sent or negative on Chinese, where the un-
derlying model, not the skill pack, sets the
ceiling: claude-haiku-4.5 far outscores
gpt-5.4-mini on Zh.QA at K=20, the largest
raw-capability gap in the multi-book table.
Fixed recipe.We hold the chunking and de-
scription recipe fixed at one widely adopted book-
to-skill procedure, so a different chunk granularity
or description-writing model might shift the bal-
ance between the three approaches.
Sample size.Our sample sizes are those
∞Bench provides, so several of our comparisons
stay within a standard error. This bound comes
from the dataset, not from LOONGDOC: the
pipeline converts any long-context reading bench-
mark into the same agentic file-system environ-
ment, so a benchmark with more questions would
tighten every estimate. We build on ∞Bench be-
cause it ships gold answers that a local determin-
istic verifier scores directly, whereas comparable
benchmarks such as NovelQA (Wang et al., 2025)
withhold their labels and score predictions only
through a third-party platform (Codabench), which
we could not fit into a controlled multi-harness
sweep.
Ethics Statement
Our study raises no direct ethical concerns. We
evaluate reading strategies on ∞Bench (Zhang
et al., 2024a), a public benchmark of long doc-
uments used under its released terms, and we in-
troduce no new human-subject data. The books
behind every subset, multiple-choice and open QA
alike, are copyrighted novels. We neither redis-
tribute their text nor release the derived skill packs;
LOONGDOCbuilds each task and pack from the
public ∞Bench release, so reproducing our re-
sults adds no copyrighted material beyond what
the benchmark already distributes.
Acknowledgments
This material is based upon work supported by UC
Noyce Initiative.
References
Anthropic. 2025a. Effective context engineering for AI
agents. Anthropic Engineering Blog.
Anthropic. 2025b. Equipping agents for the real world
with agent skills. Anthropic Engineering Blog. Open
standard published December 2025 at https://
agentskills.io/.
Yushi Bai, Xin Lv, Jiajie Zhang, Hongchang Lyu,
Jiankai Tang, Zhidian Huang, Zhengxiao Du, Xiao
Liu, Aohan Zeng, Lei Hou, Yuxiao Dong, Jie Tang,
and Juanzi Li. 2024. LongBench: A bilingual, multi-
task benchmark for long context understanding. In
Proceedings of the 62nd Annual Meeting of the As-
sociation for Computational Linguistics (V olume 1:
Long Papers), pages 3119–3137, Bangkok, Thailand.
Association for Computational Linguistics.
Yushi Bai, Shangqing Tu, Jiajie Zhang, Hao Peng, Xi-
aozhi Wang, Xin Lv, Shulin Cao, Jiazheng Xu, Lei
Hou, Yuxiao Dong, Jie Tang, and Juanzi Li. 2025.
LongBench v2: Towards deeper understanding and
reasoning on realistic long-context multitasks. In
Proceedings of the 63rd Annual Meeting of the As-
sociation for Computational Linguistics (V olume 1:
Long Papers), pages 3639–3664, Vienna, Austria.
Association for Computational Linguistics.
Gal Bakal. 2026. Knowledge activation: AI skills as the
institutional knowledge primitive for agentic software
development.Preprint, arXiv:2603.14805.
BenchFlow team. 2026. BenchFlow: framework for RL
environments for LLM agents.
9
