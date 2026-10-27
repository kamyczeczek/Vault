---
type: Concept
title: reflection_invisible_context_manager
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

# Invisible context managers are a documented failure class — the repair is visibility, not better hiding

taxonomy: #context-engineering #persistence #context-state-blindness #lossless-externalization

**Problem.** A long-running agent's context must be managed somehow. The tempting design is a
sidecar that silently manages context *without the agent knowing* — a "subconscious" that
evicts, summarizes, and relaunches sessions so the agent never spends attention on it.

**Symptom.** arXiv 2606.30005 names this exact shape as a failure class: systems that "manage
context in a layer the agent never sees." The diagnosis is not that the manager is badly
written but that it decides under information it cannot have — "a fixed rule cannot know which
evidence will matter later." The agent itself is "proprioceptively blind": from the prompt
alone it cannot infer block size, recency, or remaining budget.

**Root cause.** The keep-vs-archive decision needs runtime state that lives only in the hidden
layer. Moving the decision outside the agent does not remove the state dependency; it moves it
to a decider with strictly less context about future relevance.

**Verified repair.** VISTA exposes a runtime dashboard (per-block token usage, recency, archive
status, budget) to the agent and lets it archive bulky blocks as external payloads with stable
handles, recovering exact bytes on demand. Both resources are proved necessary:
recoverability, "because discarded evidence cannot otherwise be restored," and informative
proprioceptive state, "because a size-blind manager over-archives or under-recovers."
Training-free; beat ReAct, deletion, masking, compaction, and Claude Code on LOCA-Bench across
four backbones.

**Workspace mapping.** A corpus chunk id is a stable handle over a lossless external payload.
Querying `knowledge/graph/ask.py` instead of re-reading markdown is the same intervention at a
coarser grain: state lives outside the window and is addressable. The lesson is not "agents
must think about their own context" — it is "the agent decides, with information it can see."

**Source.** Research record `RESEARCH/2026-09-16_software-factory-slop-persistence/`, §4.
