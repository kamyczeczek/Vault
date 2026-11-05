---
type: Concept
id: 13_is_progressive_disclosure_all_you_need_for_long
title: "Is Progressive Disclosure All You Need for Long-Context Agents? (part 14/17)"
source: "Is Progressive Disclosure All You Need for Long-Context Agents"
tags: [agentic, agents, anti-leakage, context-engineering, icm, memory, planning, prompt-engineering, reflection, progressive-disclosure]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Multiple-choice task instruction (En.MC)
You are given the full text of a book and a set of
multiple-choice questions about it.
The full book text is available at /environment/book.txt.
Answer every question by choosing one of the provided options.
Each question is stored as a separate file under
/environment/questions/; each subdirectory (e.g. 42/) contains
a question.md with the question text and its answer options.
List the directory to discover all question IDs.
Output format: for each question, write your chosen option
letter (A, B, C, or D) to a plain-text file at
/logs/artifacts/questions/<QID>/answer.txt. Write one
answer.txt for every question.
Free-form QA task instruction (En.QA,Zh.QA)
You are given the full text of a book and a set of questions
about it.
The full book text is available at /environment/book.txt.
Answer every question with a short, accurate answer (one or a
few words). Each question is stored as a separate file under
/environment/questions/; each subdirectory (e.g. 42/) contains
a question.md with the question text. List the directory to
discover all question IDs.
Output format: for each question, write your answer as plain
text to /logs/artifacts/questions/<QID>/answer.txt. Write one
answer.txt for every question.
Figure 5: The task instructions handed to the agent, held fixed across the three approaches (Section 3.3). A book-QA
item maps to one of two instructions: multiple-choice for En.MC and free-form for En.QA and Zh.QA (both use
the same English instruction). The instruction carries no placeholders; only the artifacts beside book.txt in the
file system change across raw, flat, and hierarchical. At library scale the same instruction gains a short
bundle preamble and rewrites the book path to /environment/books/<label>/book.txt. The verifier
scores the written answers deterministically, so no answer-extraction model sits between the agent and the score.
models without leaking answers. We report in-
dex construction separately from per-query answer
generation: the one-time indexing cost amortizes
over every question for a book, while we measure
answer-generation latency and token cost at query
time.
B Experimental setup
Compute environment.The closed models
(gpt-5.4-mini, claude-haiku-4.5, and
the Codex backend) answer as hosted API calls, so
the harnesses only orchestrate requests; we run that
orchestration in local Docker containers at their de-
fault resource classes. Only qwen3.6-27b needs
local hardware: we serve it with vLLM on two
NVIDIA RTX 8000 GPUs, sharded with tensor par-
allelism ( -tensor-parallel-size 2 ) and
a 131 072-token context window. Across ev-
ery adapter we pin the agent packages to
pi-coding-agent 0.66.1 and pi-acp 0.0.25,
so agent-behavior changes cannot confound the
cross-harness comparison.
B.1 Single-book evaluation
We evaluate the three approaches from Sec-
tion 3.2 on three ∞Bench (Zhang et al.,
2024a) subsets that exercise book-length un-
derstanding: English multiple-choice ( En.MC),
English open QA ( En.QA), and Chinese
open QA ( Zh.QA). Three agent harnesses
(Codex, Pi, and Claude-Code) drive three mod-
els: gpt-5.4-mini, qwen3.6-27b, and
claude-haiku-4.5. Each harness runs
raw, flat, and hierarchical over the
same book, so the only variable is how the
agent reaches a passage (Section 3.3). All runs
13
