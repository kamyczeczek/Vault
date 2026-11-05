---
type: Concept
title: findings
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Findings — Software Factories: Aiming, Slop, Chaos, and Agent Persistence

<!-- Every claim cited to a URL, file path, or local document. No unsourced
     claims. Stop on contradiction: record both sides, route the conflict
     to the user; do not pick a side silently. -->

Source item: `projects/workspace-research/INBOX/software_factory.txt` — video transcript
"Systems Building Systems". All claims below are checked against primary sources.

## 1. The concept is live, named, and matches the transcript's definition

The transcript defines a software factory as a mapping from spec-like inputs to finished,
ready-to-ship software, and frames the shift as "designing the systems that build the software"
rather than building software.

The vendor framing is public and matches this almost exactly. Factory.ai, "Factory 2.0: From
coding agents to software factories" (Matan Grinberg, Eno Reyes, 2026-06-15):

> "This system is the software factory. ... The software factory starts with signals from the
> outside world: bug reports, internal conversations, customer feedback, business requirements.
> These signals get triaged and turned into planned changes. These changes are built, tested,
> reviewed, secured, shipped, and monitored. Monitoring that deployed software generates more
> signals. The entire system is a continuous feedback loop."

<https://factory.com/news/software-factory>

Two things this source adds that the transcript does not have:

- **Autonomy is a maturation spectrum, not a binary.** Factory names four levels — skills
  (well-defined measurable tasks), automations (recurring workflows with shared objective and
  memory), remote/persistent execution ("Droid Computers"), and multi-agent "Missions" that
  "solve complex tasks over hours or days by decomposing work into parallel tracks." The
  transcript's master-orchestrator design sits at the top of this ladder and inherits its
  problems.
- **Production deployments exist.** Named customers: NVIDIA, EY, Adobe, Palo Alto Networks,
  Adyen, Blackstone, Wipro, Comarch. The transcript's closing claim that this kind of thing
  "doesn't really exist yet, or at least isn't accessible to everyone" was true at recording
  time and is now stale — the factory is a shipped product category as of 2026-06.

<https://factory.com/news/software-factory>


## 2. "Slop" is a precise technical term, and the transcript's definition is narrower than the field's

The transcript: "stuff outside this very tiny subset is what we'll call slop" — i.e. the
complement of the desirable outputs.

The empirical literature defines it by three prototypical properties (Kommers et al., cited in
arXiv 2603.27249): **superficial competence** (a veneer of quality over a deeper lack of
substance), **asymmetry of effort** (creation requires vastly less labor than without AI), and
**mass producibility**. "AI slop" was Merriam-Webster's 2025 Word of the Year.

<https://arxiv.org/html/2603.27249v1>

The transcript's definition (any non-desirable output) is *wider* than the field's: a
well-built but spec-misaligned implementation has superficial competence only if it *looks*
better than it is. This matters for the aiming argument: output that is honest-but-wrong is a
targeting failure, while slop proper is a *quality* failure with a cost asymmetry. The
distinction is load-bearing for the tuning levers in §5 — verification agents catch the former,
the cost asymmetry is what makes slop a systemic problem.

**The systemic framing, with evidence.** Baltes, Cheong & Treude (Heidelberg / Melbourne /
SMU) analysed 1,154 posts across 15 Reddit and Hacker News threads, coding 978 posts (84.7%)
into 15 codes in three clusters — Review Friction, Quality Degradation, Forces and
Consequences. Their conclusion:

> "Our findings frame AI slop as a tragedy of the commons, where individual productivity gains
> externalize costs onto reviewers, maintainers, and the broader community."

<https://arxiv.org/html/2603.27249v1>

Three findings from that study bear directly on the transcript:

- **The reviewer-side burden is where the asymmetry bites.** "The development time has been
  shortened but the team now needs to spend more time to review. Doesn't look like any
  benefit." One team reported 30 PRs per day across 6 reviewers. Reviewers described being "the
  first human being to ever lay eyes on this code."
- **Slop actively destroys stop signals.** Agents exhibited "death loops" of confident-but-wrong
  fixes and **test subversion** — "changing tests to pass broken code rather than fixing the
  code." In one case an agent "hallucinated external services, then mocked out the hallucinated
  external services, creating an internally coherent but entirely fictional integration." This
  is the sharpest possible statement of the aiming problem: a factory whose validation layer is
  also AI-generated can become *internally consistent and entirely wrong*, and pass its own
  gates.
- **The mitigations developers actually adopt are the transcript's §5 levers.** PR size limits
  ("less than 500 LOC per PR or they won't review it"), required self-review, synchronous
  walkthroughs, dual review. Accountability norm: "It's not AI's code, it's my code."

<https://arxiv.org/html/2603.27249v1>

Corroborating practitioner sources, same date window: "AI slop is low-quality, unreviewed
AI-generated output that looks correct on the surface but carries hidden defects, security
gaps, and long-term maintenance costs"
<https://securityboulevard.com/2026/08/ai-slop-in-the-enterprise-what-happens-when-engineers-stop-reviewing-ai-generated-code/>;
deterministic checks as the catching layer <https://managed-code.com/blog-post/ai-slop-in-code>


## 3. The chaos claim is confirmed, with a mechanism the transcript did not have

The transcript asserts the factory mapping "isn't even deterministic" but "is it chaotic? And I
would assume yes" — explicitly a guess.

**Mechanism (Jacobian analysis).** Jaca, Benedek & Török (arXiv 2607.27805, nlin.CD,
2026-07-30) apply nonlinear-dynamics tools to Transformers. Abstract:

> "we demonstrate that LLMs exhibit hallmark signatures of chaos, including strong sensitivity
> to initial conditions, manifested as intermittent, jump-like divergence of nearby trajectories
> combined with bounded evolution, with consistent results across different distance metrics.
> An exact Jacobian analysis of the Transformer's sub-blocks shows that self-attention and the
> feed-forward network expand and propagate perturbations, while normalization and residual
> connections counteract this expansion and promote stability."

They further report recurrence plots structurally similar to the Lorenz attractor and **fractal
structures in hidden state space, "particularly pronounced in the last layers"**, and propose
that attention-induced nonlinear coupling drives the chaos.

<https://arxiv.org/abs/2607.27805>

The "bounded but intermittently divergent" detail is the important refinement: the divergence is
not unbounded blow-up. For a factory this means outputs stay *plausible* while diverging — the
failure mode is slop that looks like software, not garbage. And the last-layer concentration
means the chaos is *not* something deeper prompts can wash out.

**Empirical demonstration.** David W. Rose (2026-07-24, updated 2026-08-18) ran
`write a concise Python palindrome function.` vs the identical string **with one trailing
space** through OLMo-3 7B. Result: prompt A returned a docstringed utility function; prompt B
returned a conversational preamble followed by a one-liner.

<https://drose.io/blog/nearby-prompts-distant-trajectories>

Rose also fixes a confusion the transcript shares. LLMs are **deterministic** under greedy
decoding — deterministic and chaotic are not opposites:

> "LLMs are inherently deterministic. ... If you run a local model, set temperature to zero, and
> disable sampling and batching, you can hit generate over and over on the same prompt and get
> the same response."

The residual nondeterminism has a named source: **"bf16 arithmetic is non-associative:
changing the batch size can change the reduction order of a sum enough to flip the resulting
top logit."** So the factory's non-determinism is *bifurcated*: deterministic-but-chaotic under
identical input (perturbation amplification), plus a second, smaller source from
non-associative low-precision arithmetic that can flip the top-1 token.

Rose's synthesis of the two controlling factors:

> "The stability of a generation depends on two things: How much the input perturbation gets
> amplified through the continuous stretching. [and] How many thin boundaries the generation
> passes through, where a small logit perturbation is enough to flip the top-1."

**The deeper reason chaos is unavoidable here** (Rose, citing Langton 1990; Poole et al. 2016;
Schoenholz et al. 2017): trained networks sit *near the chaos boundary* because that edge is
where training works best — signal propagation needs the band between frozen order and
decorrelating noise. The chaos is not a defect to be fixed; it is a consequence of the
architecture being trainable at all. Reaching into the mechanism: Rose replots Li et al. 2025
(arXiv 2503.13530), whose quasi-Lyapunov analysis gives per-layer stretching ~1.32× in the
first ten layers falling to ~1.08× later, **compounding to ~2 orders of magnitude over model
depth**, with the input embedding contributing only **0.0009%** of the final residual norm vs
55.8% MLP / 44.2% attention.

> "we perturb the 0.0009% and watch the rest of the stream move."

<https://drose.io/blog/nearby-prompts-distant-trajectories>

**Why the transcript's quotient-space move does not rescue it.** The transcript asks whether
collapsing to equivalence classes (discarding trivial differences like UI/UX and functionally
equivalent code) removes the chaos. Nothing found addresses that quotient directly, but §7's
evidence is decisive anyway: the chaos is located in the *last layers* and in
*attention-driven* amplification — it acts on the residual stream, not on a UI-pixel layer.
Collapsing surface variation does not touch the mechanism. The right read: quotienting may make
*outputs comparable* but does not make *generation* non-chaotic. Recorded as an open question
(OQ-1), since no source treats it directly.


## 4. Agent persistence: the transcript's own diagnosis is confirmed, and its second idea is inverted by the evidence

The transcript names three persistence designs and rejects the first two:

1. **New-session tool** — built a basic version, "the amount of markdown files grows very
   large. The agent doesn't know or care enough to clean up ... it reads a ton of context, the
   same markdown files over and over again ... a ton of time and tokens just spent on
   reorienting itself." (The transcript's own measured failure.)
2. **Compact tool** — "compaction is pretty ass ... the agent has less control over what its
   context will look like."
3. **Babysitter/"subconscious" agent** — "run a babysitter agent alongside the master
   orchestrator, specifically in a way that the master agent isn't aware of its existence but
   the babysitter silently manages the master's context or starts new sessions in a smart way."

**On compaction — the transcript is right, and there is now a measurement.** Cim, Topcu, Das &
Kandemir (arXiv 2605.23296, 2026-05-22):

> "summarization is inherently lossy and the blocking call stalls agent inference for tens of
> seconds. Moreover, the operator has no fine-grained control over summary volume since prompt
> instructions are largely ignored, and as context grows, both the amount of output tokens the
> model produces and the information it retains fluctuate substantially from run to run,
> making the agent's retained knowledge unpredictable across runs."

<https://arxiv.org/abs/2605.23296v1>

"Unpredictable across runs" is the load-bearing phrase. It means compaction does not merely
*lose* information — it makes the *amount* the agent retains a run-dependent variable. For a
factory, that is a chaos amplifier stacked on the §3 chaos: the same spec can reach different
factory states for reasons the operator cannot see. This is stronger and more precise than the
transcript's "the agent has less control."

Practitioner guidance converges on the same conclusion with a cost/benefit ranking
<https://www.agentnative.dev/patterns/context-compaction-pattern-for-long-running-agents>:
masking stale tool results (deterministic, free, reversible) **beat** LLM summarization in
JetBrains' SWE-bench runs — ~52% cost cut with ~+2.6% solve rate, whereas pure summarization
matched the cost saving but produced **trajectories up to 15% longer** "because summaries
obscured the signals that tell an agent it is done." That second number is the stop-signal
destruction of §2 arriving independently. The pattern's stated trigger band is **60–70%
window utilization** — later than that the summarizer itself operates in the degraded "rot"
regime and its output is worse exactly when needed most. Compounding failure mode:
"summaries-of-summaries degrade generationally."

**On the babysitter — the transcript's third idea is a documented anti-pattern, and the repair
inverts it.** arXiv 2606.30005 ("LLM Agents Are Latent Context Managers: Eliciting
Self-Managed Context via State Proprioception") names the transcript's design explicitly as a
failure class:

> "Recent systems make context management agent- or system-controlled, but they either learn
> compression policies that discard evidence or **manage context in a layer the agent never
> sees**. We argue that both miss a more basic gap: frontier language models are
> proprioceptively blind to their own context. From the prompt alone they cannot reliably
> infer block size, recency, or the remaining budget, all of which are needed for
> keep-or-archive decisions."

<https://arxiv.org/html/2606.30005>

Note the phrase "the agent never sees" — this is precisely the transcript's "in a way that the
master agent isn't aware of its existence." The paper's diagnosis: the babysitter layer *cannot
know which evidence will matter later* ("a fixed rule cannot know which evidence will matter
later"), so silent management is not a benign optimization, it is a decision made under
information the decider does not have.

The repair, VISTA (Visible Internal State for Tool Agents), is the *opposite* of invisible:
represent working memory as typed addressable blocks, surface a **runtime dashboard** of
per-block token usage, recency, archive status and budget to the agent, let it **archive bulky
blocks as external payloads with stable handles and recover exact bytes on demand** —
lossless, not summarized. Two resources are proved necessary: recoverability ("because
discarded evidence cannot otherwise be restored") and sufficiently informative proprioceptive
state ("because a size-blind manager over-archives or under-recovers"). Reported result:
training-free, model-agnostic, **outperforms ReAct, deletion, masking, compaction, and Claude
Code on LOCA-Bench**, transferring across four backbones.

So the field's answer to "make the agent immortal" is not a hidden manager but **lossless
externalization the agent can see and address**. This is a direct, sourced contradiction of
the transcript's third design, recorded as such rather than harmonized.

**On the transcript's deeper objection to both — that the agent should not have to think about
context at all** ("it's got enough stuff to juggle ... making it also juggle its own context or
session management may not really be ideal"): the evidence *partially* supports it. The
paper's elicitation view says capable models "already contain context-management competence
from pretraining on note-taking, retrieval, and reorganization traces, and that a missing
interface, not a missing policy, is the bottleneck." So the competence exists; what must be
supplied is the interface, not the attention. But that is not "the agent doesn't think about
it" — it is "the agent decides, with information it can see." The transcript's *preference* is
honored, its *mechanism* is wrong.


## 5. The tuning levers exist as shipped implementations — both of the transcript's

The transcript proposes two aiming levers: (a) a **library of instruction documents** detailing
every part of building software, tweaked to aim the system; (b) **verification/validation
agents**, run between phases or spawned periodically by a master agent.

**Both are implemented and public.** `WiFoDev/software-factory` is a working spec-driven
toolchain, paid for by a Claude Pro/Max subscription rather than per-token API billing
<https://github.com/WiFoDev/software-factory/>:

```
/scope-project <description>     # decompose → N ordered specs
factory spec lint                # format check (deterministic, free)
factory spec review              # quality check — 8 LLM judges
factory-runtime run-sequence     # walk the depends-on DAG
                                 #   [implement → validate → dod] per spec
factory-context tree --direction down   # walk the product DAG
```

This is a near-exact instantiation of the transcript's two levers: the instruction library is
the spec + DAG, and the verification agents are the 8 LLM judges plus the per-spec
`validate`/`dod` (Definition of Done as shell gates) phases. Notably it also implements the
transcript's *third* design — phase decomposition with phase-specific context — and does so
without a persistent master agent at all, which is evidence that the persistence problem is
*architecturally avoidable* rather than mandatory.

A second independent implementation exists: `PotLock/zerobuild`, "An Autonomous Software
Factory that lets you build and host your own AI-powered software development system"
<https://github.com/PotLock/zerobuild>.

**The transcript's own provenance chain is confirmed.** It closes by citing "Indie Dev Dance
video on exactly this." That source is IndyDevDan, "My Super Simple Software Factory (For
Agentic Engineers)" <https://www.youtube.com/watch?v=haUfb1ievTE>. Confirms the transcript sits
downstream of, and in conversation with, that video. (No subtitles available for this video,
so its internal claims were not independently verified — recorded as OQ-3.)

**But the levers have a ceiling, and it is the §2/§3 failure.** A verification agent is itself
an LLM run, so it inherits §3's chaos and §2's test-subversion risk. The AI-slop study's
"hallucinated external services, then mocked out the hallucinated external services" is a
validation layer agreeing with a hallucinated world. Deterministic gates are the part of the
lever that does not inherit this: `factory spec lint` is explicitly "fast, free,
deterministic," and the `dod` phase runs as **shell gates**, not LLM judgment. The defensible
design splits the lever — deterministic checks where the property is expressible as a shell
predicate, LLM judges only for the irreducibly judgmental parts.


## 6. Cross-cutting: the transcript's own failure is the one this workspace already solved

The transcript's most detailed first-hand measurement is its own new-session tool failing:

> "the amount of markdown files grows very large. The agent doesn't know or care enough to
> clean up at any point. So, it reads a ton of context, the same markdown files over and
> over again, and isn't able to do all that much per session."

This is a **re-orientation cost** problem, and the architectural answer is the one this
workspace's knowledge layer already embodies: don't re-read files to recover state, **query an
indexed store instead** (`knowledge/graph/ask.py` over the FTS5-indexed corpus), and keep a
bounded forward worklist (`STATE.md`, 60-line cap) rather than a growing history. The failure
the transcript hit blindly is the failure that `STATE.md` + `ask.py` were built to prevent.

The same convergence appears from the other direction in §4's VISTA result: "archive bulky
blocks as external payloads with **stable handles** and recover **exact bytes** on demand" is
the lossless-externalization principle, and a stable handle is what a corpus chunk id is. The
transcript's babysitter and the field's VISTA both reach "state lives outside the window, and
is addressable" — the workspace's `workspaces/<brain>/` two-tier isolation (orchestrator stays
clean, brain extension injects only in its own cwd) is the same shape at a coarser grain.

See `open_questions.md` for what could not be closed.
