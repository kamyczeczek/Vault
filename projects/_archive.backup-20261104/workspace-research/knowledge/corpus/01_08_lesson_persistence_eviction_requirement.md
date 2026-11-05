---
type: Concept
id: 01_08_lesson_persistence_eviction_requirement
title: "ExpeL's ledger is the mechanism, but eviction is what makes a stored lesson trustworthy (part 2/2)"
source: "08_lesson_persistence_eviction_requirement.md"
tags: [context-engineering, memory, reflection]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

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
