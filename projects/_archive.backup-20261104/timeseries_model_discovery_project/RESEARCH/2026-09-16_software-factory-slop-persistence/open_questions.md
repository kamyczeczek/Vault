---
type: Concept
title: open_questions
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Open Questions — Software Factories: Aiming, Slop, Chaos, and Agent Persistence

<!-- Questions that remain unanswered, each with the reason each could not be
     resolved (missing access, conflicting sources, out of scope). -->

## OQ-1. Does quotienting the output space remove the chaos?

**The transcript's move:** collapse outputs to equivalence classes, discarding trivial
differences (UI/UX, functionally equivalent code), then ask whether *that* mapping is chaotic.

**Why unresolved:** no source found treats this quotient directly. The nearest evidence is
indirect and points one way: arXiv 2607.27805 locates the chaos in the **last layers** and in
attention-driven amplification on the residual stream — not in a surface or presentation layer
— and Rose's "thin boundaries" framing makes chaos a property of the generation trajectory,
not of comparing two finished artifacts. The plausible read is that quotienting makes *outputs
comparable* without making *generation* non-chaotic, but that is an inference, not a finding,
and `findings.md` §3 labels it as such.

**What would settle it:** a chaos measurement run over a semantic-equivalence metric rather
than token or hidden-state distance. Not found.

<https://arxiv.org/abs/2607.27805>
<https://drose.io/blog/nearby-prompts-distant-trajectories>


## OQ-2. Is "aiming" even a well-posed optimization target under chaos?

**Why unresolved:** the transcript asserts aiming is "the slow, expensive, and difficult part"
but never states what aiming *is* — no loss function, no acceptance metric, no notion of
distance from the desirable subset. The evidence found makes the question harder rather than
answering it: if retained context after compaction is "unpredictable across runs"
(arXiv 2605.23296) and generation is chaotic (arXiv 2607.27805), then a tuning parameter can
have a *run-dependent* effect on output, which is a different problem from a badly-set
parameter.

**What is known:** deterministic gates are the one part of the aiming lever that does not
inherit the chaos — `factory spec lint` is deterministic, `dod` runs as shell gates
(<https://github.com/WiFoDev/software-factory/>). So aiming decomposes into a deterministic
part (expressible as a predicate) and a chaotic part (LLM judgment), and only the second is
uncontrolled.

**What would settle it:** a measurement of tuning-parameter sensitivity on a real factory —
does tweaking the instruction library move the output distribution measurably and
repeatably? Not found; the transcript offers no numbers.


## OQ-3. What does the transcript's cited source actually claim?

**Why unresolved:** the transcript closes by attributing its framing to "Indie Dev Dance video
on exactly this," identified as IndyDevDan, "My Super Simple Software Factory (For Agentic
Engines)" (<https://www.youtube.com/watch?v=haUfb1ievTE>). **No subtitles or transcript are
available for this video** (verified: `yt-dlp --write-sub --skip-download` returned "There are
no subtitles for the requested languages"), so its internal claims could not be read, only its
existence and title confirmed. The transcript is therefore confirmed *downstream of* the video,
but not *consistent with* it.

**What would settle it:** a transcript via audio transcription (the agent-reach `youtube`
backend reports transcription capability with the `openai` backend) or a published written
summary. Not attempted — out of scope for a research pass, and the transcript's own claims were
the subject under verification.


## OQ-4. Do the empirical slop and chaos results transfer to frontier closed models?

**Why unresolved:** the chaos evidence is largely on open weights — Rose's one-trailing-space
result is **OLMo-3 7B**, and arXiv 2607.27805 analyses Transformer architecture generally
(architecture-level transfer is a reasonable inference, but the paper's own measurements are on
specific backbones). The compaction unpredictability (arXiv 2605.23296) spans 8B–120B, dense
and MoE, reasoning and non-reasoning — the broadest coverage found. The AI-slop study
(arXiv 2603.27249) is about developer *discourse*, not model measurements at all, so it carries
no backbone assumption.

**Why this matters for the workspace:** the corpus's own S-43/S-44 work is model-agnostic
protocol work, whereas a chaos claim is a claim about a specific model's dynamics. A frontier
closed model could in principle sit further from the chaos boundary. Nothing found measures
this, and closed-model internals are not inspectable, so this is likely to stay open.

<https://arxiv.org/abs/2607.27805>
<https://arxiv.org/abs/2605.23296v1>
<https://arxiv.org/html/2603.27249v1>
