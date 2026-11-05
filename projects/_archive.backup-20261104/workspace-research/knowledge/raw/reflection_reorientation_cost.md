---
type: Concept
title: reflection_reorientation_cost
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

# Re-orientation cost is the real persistence failure — bounded state plus query beats growing files

taxonomy: #persistence #reorientation-cost #query-over-read #liveness

**Problem.** Extending an agent's life by relaunching sessions fails in a specific, measurable
way — and it is not the session boundary itself.

**Symptom (first-hand).** The source transcript built a new-session tool and measured the
failure: "the amount of markdown files grows very large. The agent doesn't know or care enough
to clean up at any point. So, it reads a ton of context, the same markdown files over and over
again, and isn't able to do all that much per session." Session restart works; state recovery
does not.

**Root cause.** State is held in growing un-indexed files, and each session recovers it by
reading. Cost grows with accumulated history while work-per-session shrinks. The fix is not a
better handoff prompt — the transcript tried writing better launch prompts and found the cost
was in the re-orientation, not the prompt.

**Verified repair (three converging sources).**
- Bounded forward worklist: `STATE.md` holds present-tense state capped at 60 lines, enforced
  by `PROCESS/check_state.py`. State recovery is a bounded read, not a growing one.
- Query over read: `knowledge/graph/ask.py` against the FTS5-indexed corpus. Recovering state
  becomes a bounded query, not a file scan.
- Lossless externalization with stable handles: arXiv 2606.30005's VISTA archives blocks as
  external payloads with stable handles and recovers exact bytes on demand — the same
  invariant as a corpus chunk id. "Notes survive compaction losslessly; summaries do not."

**Boundary.** This is the architectural alternative to the phase-decomposition design: WiFoDev's
factory runs `[implement → validate → dod]` over a depends-on DAG with no persistent master
agent at all, which is evidence the persistence problem is architecturally avoidable rather
than mandatory.

**Source.** Research record `RESEARCH/2026-09-16_software-factory-slop-persistence/`, §4–§6.
