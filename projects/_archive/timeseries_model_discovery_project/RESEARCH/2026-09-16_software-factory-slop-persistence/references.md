---
type: Concept
title: references
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# References — Software Factories: Aiming, Slop, Chaos, and Agent Persistence

<!-- Flat list of every external source consulted: URL + access date +
     1-line summary. Local sources: file path + access date. -->

Access date for all sources: **2026-09-16** unless noted.

1. **`projects/workspace-research/INBOX/software_factory.txt`** — local, accessed 2026-09-16.
   The source item under investigation: video transcript "Systems Building Systems" on software
   factories, slop, chaotic mappings, agent persistence, and aiming/tuning.

2. **Factory 2.0: From coding agents to software factories** — Matan Grinberg, Eno Reyes,
   Factory.ai, 2026-06-15. <https://factory.com/news/software-factory>
   The vendor definition of the software factory as a continuous signal→triage→build→ship→
   monitor→signal loop; three requirements (model independence, sovereign intelligence,
   continual learning); a four-level autonomy maturation spectrum; named production customers.

3. **"An Endless Stream of AI Slop": The Growing Burden of AI-Assisted Software Development** —
   Baltes, Cheong, Treude, arXiv 2603.27249v1 [cs.SE], 2026-03-28.
   <https://arxiv.org/html/2603.27249v1>
   Qualitative study of 1,154 posts / 15 threads → 15 codes in 3 clusters; frames AI slop as a
   tragedy of the commons; documents reviewer burden, test subversion, "hallucinated then mocked
   external services," and the mitigations developers adopt (PR size limits, walkthroughs).

4. **Chaos in reason: How chain-of-thought LLMs can look for an answer** — Jaca, Benedek,
   Török, arXiv 2607.27805 [nlin.CD, cond-mat.dis-nn], 2026-07-30.
   <https://arxiv.org/abs/2607.27805>
   Jacobian analysis: LLMs show sensitivity to initial conditions with intermittent, jump-like
   divergence and bounded evolution; self-attention and FFN expand/propagate perturbations while
   normalization and residual connections bound them; fractal structure concentrated in last
   layers; Lorenz-like recurrence plots.

5. **Are LLMs Chaotic? / Nearby Prompts, Distant Trajectories** — David W. Rose, drose.io,
   2026-07-24, updated 2026-08-18. <https://drose.io/blog/nearby-prompts-distant-trajectories>
   Empirical: one trailing space flips OLMo-3 7B's output shape. Establishes LLMs are
   deterministic under greedy decoding (chaos ≠ randomness), names bf16 non-associativity as a
   top-1 flip source, and synthesizes that trained networks sit near the chaos boundary because
   that is where training works (Langton 1990; Poole 2016; Schoenholz 2017).

6. **Parallel Context Compaction for Long-Horizon LLM Agent Serving** — Cim, Topcu, Das,
   Kandemir, arXiv 2605.23296v1 [cs.AI], 2026-05-22. <https://arxiv.org/abs/2605.23296v1>
   LLM-based summarization is lossy, blocking, and "the information it retains fluctuates
   substantially from run to run, making the agent's retained knowledge unpredictable across
   runs"; proposes parallel compaction for operator control over summary volume.

7. **Context Compaction Pattern for Long-Running Agents (2026)** — Agent Native,
   2026-07-26. <https://www.agentnative.dev/patterns/context-compaction-pattern-for-long-running-agents>
   Practitioner pattern: observation masking beat LLM summarization in JetBrains SWE-bench
   (~52% cost cut, +2.6% solve vs summarization matching cost but trajectories up to 15%
   longer); 60–70% trigger band; keep-verbatim zones; failure-mode catalogue including
   summary-induced amnesia and lost stop signals.

8. **LLM Agents Are Latent Context Managers: Eliciting Self-Managed Context via State
   Proprioception (VISTA)** — arXiv 2606.30005. <https://arxiv.org/html/2606.30005>
   Names the transcript's invisible-babysitter design as a failure class ("manage context in a
   layer the agent never sees"); diagnosis is proprioceptive blindness; VISTA surfaces a
   runtime dashboard plus lossless archive-with-stable-handles, beating ReAct, deletion,
   masking, compaction and Claude Code on LOCA-Bench.

9. **`WiFoDev/software-factory`** — GitHub, accessed 2026-09-16.
   <https://github.com/WiFoDev/software-factory/>
   Working spec-driven factory: `factory spec lint` (deterministic) → `factory spec review`
   (8 LLM judges) → `factory-runtime run-sequence` walking a depends-on DAG with
   [implement → validate → dod] per spec, dod as shell gates; Claude Pro/Max subscription
   billing instead of per-token.

10. **`PotLock/zerobuild`** — GitHub, accessed 2026-09-16. <https://github.com/PotLock/zerobuild>
    Second independent implementation: "An Autonomous Software Factory that lets you build and
    host your own AI-powered software development system."

11. **My Super Simple Software Factory (For Agentic Engineers)** — IndyDevDan, YouTube,
    `haUfb1ievTE`. <https://www.youtube.com/watch?v=haUfb1ievTE>
    The transcript's cited source of inspiration ("Indie Dev Dance video on exactly this").
    Existence and title confirmed; **no subtitles available**, so its internal claims were not
    verified (OQ-3).

12. **AI Slop in the Enterprise: What Happens When Engineers Stop Reviewing AI-Generated Code** —
    Security Boulevard, 2026-08.
    <https://securityboulevard.com/2026/08/ai-slop-in-the-enterprise-what-happens-when-engineers-stop-reviewing-ai-generated-code/>
    Corroborating practitioner framing: slop as surface-correct output carrying hidden defects,
    security gaps, and long-term maintenance costs.

13. **AI slop in code: what it looks like and how to stop it landing in your codebase** —
    managed-code.com, accessed 2026-09-16. <https://managed-code.com/blog-post/ai-slop-in-code>
    Corroborating: which *deterministic* checks catch AI slop in code.
