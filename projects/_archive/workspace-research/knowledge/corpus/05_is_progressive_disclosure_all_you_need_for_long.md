---
type: Concept
id: 05_is_progressive_disclosure_all_you_need_for_long
title: "Is Progressive Disclosure All You Need for Long-Context Agents? (part 6/17)"
source: "Is Progressive Disclosure All You Need for Long-Context Agents"
tags: [agentic, agents, anti-leakage, context-engineering, icm, memory, planning, prompt-engineering, reflection, progressive-disclosure]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

book-nav/
1 · always in context
SKILL.md  (meta / router)
name: book-navigation
description: Navigate Frankenstein
  (31 chapters, each a skill)
2 · loaded on activation

---
Instructions to use these chapter Skills
---
chapter-01/
1 · always in context
SKILL.md (frontmatter)
name: book-chapter-01
description: Robert Walton writes from
the Arctic; rescues Victor from the
ice.
2 · loaded on activation
SKILL.md body:
Letter 1 — To Mrs. Saville, England.
You will rejoice to hear that ...
           ...   chapter-31/
always in context on activation on demand
Figure 2: Thehierarchicalpack.
the agent navigate, host a skill pack the agent must
discover and open, or grow the corpus past a single
book. Our questions require all three. We there-
fore rebuild ∞Bench (Zhang et al., 2024a) into
LOONGDOC, an interactive environment. Built on
BenchFlow (BenchFlow team, 2026), LOONGDOC
runs any harness that implements the Agent Client
Protocol (ACP) (Zed Industries, 2025) against a
sandboxed task and records what it does. Each
∞Bench question, multiple-choice (MC) or open
QA, becomes a task the agent acts on through a file
system rather than a fixed context, and every run
leaves a scored trajectory we can inspect (Figure 3).
BenchFlow already hosts SKILLSBENCH(Li et al.,
2026), a widely adopted benchmark for general-
purpose agent skills (Qwen Team, 2026; Tencent
Hy Team, 2026); LOONGDOCadds a long-context
reasoning environment to the same runtime.
From a benchmark item to an agent task.A
LOONGDOCtask pairs a prompt with a sandboxed
file system and a verifier that scores the result, the
∞Bench item: book(s) + question
Sandbox file system
book files + book-to-skill pack
Agent (ACP harness)
read / grep / open
Verifier: answer match
Reward + trajectory logged
task
prompt files
answer
score
Figure 3: The LOONGDOCenvironment: an ∞Bench
book-QA item becomes a BenchFlow task the agent
solves through a sandboxed file system.
shape TERMINAL-BENCH(Merrill et al., 2026)
and SKILLSBENCH(Li et al., 2026) establish for
agent evaluation. We adopt it to turn∞Bench from
a static probe into an agent environment, mapping
one ∞Bench item onto one task. We write the
book into the sandbox as files, or the whole bundle
at library scale, and hand the agent the question
as its prompt. Under the disclosure approaches
of Section 3, we also stage a skill pack for the
agent to discover through BenchFlow’s native sup-
port for agent skills. The verifier then reads the
agent’s final answer and returns a score. Because
the prompt says nothing about the book, the agent
must reach the text through the file system, which
makes raw-document access and progressive dis-
closure comparable conditions inside one harness.
Free-form navigation, recorded in full.Be-
cause the book lives on disk, the agent chooses
how to reach it, and any ACP-compatible harness
can drive the environment. In our runs, Codex,
Pi, and Claude-Code read, grep, and open files at
will rather than working from a context fixed in
advance. Every rollout returns the whole trajectory:
the tool calls the agent issued, the files it opened,
and the tokens it spent at each step. This record
lets us explain results, not just report them: the
bare Codex trajectory, for instance, greps the raw
text for the entities each question names and reads
only the matched passages (Section 5), behavior
the answer string alone would hide.
A score that doubles as a reward.The verifier
5
