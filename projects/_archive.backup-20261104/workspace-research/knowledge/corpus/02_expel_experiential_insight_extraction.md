---
type: Concept
id: 02_expel_experiential_insight_extraction
title: "ExpeL: LLM Agents Are Experiential Learners"
source: "arxiv 2308.10144 (Zhao et al., AAAI 2024)"
tags: [reflection, agents, memory, self-evolution, retrieval, evaluation]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

# ExpeL — turn error trajectories into cross-task insights with a voting ledger

**Core claim:** Reflexion's failure is scope — it reflects within a single task and its memory dies with that
task. ExpeL makes error-learning *persist across tasks* by separating two phases: gather raw experience, then
extract reusable insights from it. No parameter updates, so it works on closed models.

**Three stages:**
1. **Gather.** A Reflexion-style loop collects successes *and failures* into an experience pool `B`, retrying
   up to `Z` times. Deliberately keeping the failures is what makes insight extraction possible — failures
   alone give no contrast; success/failure *pairs* on the same task do.
2. **Extract.** An insight-extraction LLM maintains a set of insights `ι` with four operators:
   **ADD**, **EDIT**, **UPVOTE**, **DOWNVOTE**. New insights start at importance 2, increment on upvote/edit,
   decrement on downvote, and are *evicted at zero*. This is the recurrence-prevention mechanism with a
   guard attached: a wrong lesson does not persist forever, it can be outvoted and removed by later evidence.
3. **Apply.** At inference the task spec is prepended with the full insight list, plus top-k similar
   successful trajectories retrieved by task similarity (Faiss + all-mpnet-base-v2).

**The key design choice for "making errors not come back."** Insights come from two contrasts:
- a *failed* trajectory vs a *successful* trajectory for the same task — isolates exactly which actions were
  the wrong ones;
- `L` successes from *different* tasks — surfaces shared good practice.

The upvote/downvote ledger is what makes this self-correcting rather than self-reinforcing. The authors state
the reason explicitly: *"even successful trajectories can be suboptimal and mislead the generated insights."*
A lesson derived from a lucky success can be wrong, and the ledger can purge it. Reflexion has no such mechanism.

**Results:** consistent improvement as experience accumulates across HotpotQA, AlfWorld, WebShop; insights
transfer forward to a target task distribution with minimal target examples.

**Documented limitation:** insight set grows monotonically in practice and the paper notes retrieval (not
concatenation) will be needed to manage the context window as it scales.
