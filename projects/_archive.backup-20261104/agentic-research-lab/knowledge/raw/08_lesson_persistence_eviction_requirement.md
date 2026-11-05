---
type: Concept
title: 08_lesson_persistence_eviction_requirement
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# ExpeL's ledger is the mechanism, but eviction is what makes a stored lesson trustworthy

**Core claim (recurrence-prevention mechanism, stated as a requirement):** documenting an error into memory
prevents its recurrence **only if the stored lesson can be removed when it turns out to be wrong**. ExpeL
(`02_expel_experiential_insight_extraction`) has this mechanism; Reflexion (`01_reflexion_verbal_reinforcement`)
does not; Honest Lying (`04_honest_lying_memory_confabulation`) shows what the absence costs. This note
separates the mechanism from the paper and states it as a design requirement for any error-logging system.

**The asymmetry that makes eviction necessary.** A stored lesson has two properties a fresh observation does
not: it is **retrieved by default** (it conditions every future trial that matches), and it accumulates an
**appearance of authority** from having survived. Both properties amplify a wrong lesson the same way they
propagate a right one. Honest Lying's measured severity — in 16 frozen ALFWorld environments, **0 of 121
reflections mentioned the correct target object** — is what an eviction-free reflection ledger converges to:
not a missing lesson, but an confidently wrong one that is re-read on every trial (RRR 0.64).

**ExpeL's specific operators.** Insights `ι` start at importance **2**. `ADD` introduces; `UPVOTE` and `EDIT`
increment; `DOWNVOTE` decrements; an insight is **evicted at zero**. This is the mechanism that makes the
ledger self-correcting rather than self-reinforcing, and the authors state the reason explicitly:
*"even successful trajectories can be suboptimal and mislead the generated insights."* A lesson derived from
a lucky success can be wrong, and the ledger can purge it. Reflexion's memory has no equivalent — its
reflections accumulate with no quality control.

**But eviction is not sufficient on its own (the honest limit).** ExpeL's authors note the insight set grows
**monotonically in practice** and that retrieval — not concatenation — will be needed to manage context as it
scales. So the ledger solves *wrong lessons* but not *volume*: an unbounded growing ledger of correct-but-
marginal lessons still floods the retrieval surface. Two independent problems, two independent mechanisms
(score-based eviction vs. retrieval) — solving one does not solve the other.

**Why persistence across tasks is the other half of recurrence prevention.** ExpeL's failure-to-learn
diagnosis of Reflexion is scope: Reflexion reflects within a single task and its memory dies with that task,
so a lesson learned never becomes a lesson applied elsewhere. ExpeL's three stages — **gather** (collect
successes **and failures**, retrying up to `Z`), **extract** (the voting ledger), **apply** (prepend insights
+ retrieve top-k similar successful trajectories via Faiss + all-mpnet-base-v2) — are what make error-learning
**persist across tasks**. Keeping the failures is deliberate: failures alone give no contrast;
success/failure **pairs** on the same task isolate exactly which actions were the wrong ones.

**Design requirements derived (for any error-logging / recurrence-prevention system).**
1. **Eviction must exist** — a lesson with no removal path is permanent. Score it, decay it, or require
   re-validation; an append-only error log violates this by construction.
2. **Eviction must be evidence-driven**, not time-driven. ExpeL's downvote-to-zero is a function of later
   experience contradicting the lesson. Time-based expiry removes correct lessons and keeps confident
   falsehoods that were stored recently.
3. **Contrast must be stored, not just the failure.** A lone failure record supports no diagnosis. Store the
   failed trajectory beside a successful one for the same task — that is what makes the root cause
   extractable rather than guessed.
4. **Storage and retrieval are separate problems.** A correct, evictable, well-contrasted lesson set still
   floods the context window at scale; retrieval over the ledger is a separate requirement from the ledger's
   correctness.
5. **Apply must be on-task-similarity**, not blanket prepending. ExpeL retrieves top-k similar trajectories;
   blanket injection reintroduces context flooding as a failure mode.

**Grounding chain.** This requirement is the mechanism-level statement of `04_honest_lying`'s measured
failure, operationalized by `02_expel`'s ledger, and it is the property that `01_reflexion` lacks by design.
