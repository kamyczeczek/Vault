---
type: Concept
id: 14_is_progressive_disclosure_all_you_need_for_long
title: "Is Progressive Disclosure All You Need for Long-Context Agents? (part 15/17)"
source: "Is Progressive Disclosure All You Need for Long-Context Agents"
tags: [agentic, agents, anti-leakage, context-engineering, icm, memory, planning, prompt-engineering, reflection, progressive-disclosure]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Single-book task
/environment/ read-only mount, staged by the adapter
|-- book.txt full book text
‘-- questions/
|-- 42/question.md question text (plus options for MC)
‘-- .../ one directory per question ID
/logs/artifacts/questions/ written by the agent
‘-- 42/answer.txt one answer.txt per question ID
Library-scale (K-book) task
/environment/ read-only mount, staged by the adapter
|-- corpus-index.md one-line summary of each member book
|-- books/
| |-- A/book.txt full text of book A
| ‘-- B/book.txt full text of book B
‘-- questions/
|-- A_42/question.md question IDs carry the book label
‘-- B_157/question.md
/logs/artifacts/questions/ written by the agent
|-- A_42/answer.txt answers carry the same label prefix
‘-- B_157/answer.txt
Figure 6: Sandbox layout the agent sees, for a single-book task (top) and a K-book library task (bottom).
The adapter stages the read-only /environment tree; the agent writes one answer.txt per question un-
der /logs/artifacts/questions, and the deterministic verifier reads those files (Section A.1). Only the file
system changes across raw, flat, and hierarchical; the routing artifacts sit beside book.txt and are omit-
ted here. At library scale the books move under /environment/books/<label>/, a corpus-index.md
lists them, and every question and answer identifier gains the book label as a prefix.
set concurrent_task=1 to avoid Docker
timeouts.
Retrieval baseline.The three agentic ap-
proaches all keep the document in the agent’s reach
and let it read on demand. To place them against
the classical alternative, we add hybrid-rag,
which replaces in-context reading with retrieval-
augmented generation: it builds a per-document
index, reranks the passages most relevant to the
question, and feeds only that evidence to the an-
swer model. We collect hybrid-rag on both
qwen3.6-27b and gpt-5.4-mini across all
three subsets as a second-model check.
C Additional experimental results
C.1 Corpus scaling on the Pi harness
In Table 3 we add the Pi harness to the
corpus-scaling study of Section 5.2, run on
gpt-5.4-mini in the same setting as Table 2.
For Pi we report all three subsets; En.MC is the
axis it shares with the Codex grid of Table 2, so
the strong- and weak-navigator harnesses meet
there. Codex is the strong-navigator end of the
scaling story and Pi the weak-navigator end, and
the two bracket the harness-dependence claim.
On En.MC, flat leads raw at every K under
Pi, whereas under Codex the same pack trails
at K=5 and only pulls ahead once the corpus
is large. The weaker the agent’s native naviga-
tion, the earlier the skill pack earns its keep. On
En.MC, Pi also echoes the routing-depth result: its
hierarchical pack is the worst configuration
at K=20, below even raw, under the same always-
loaded-index pressure that sinks hierarchical
on Codex open QA. Open QA reverses this depth
ordering. On Zh.QA, flat drags below raw at
every K and collapses to 0.137 at K=20, while
hierarchical holds the best cell there at0.330;
on En.QA, hierarchical leads at K=10 and
stays above raw at K=20. Where the corpus is
large and the questions are open, the extra routing
level that hurts En.MC recovers, so depth is a scale-
and task-specific effect rather than a uniform cost.
C.2 TheEn.QAscaling frontier
The main text draws Figure 4 for En.MC and reads
the disclosure effect on En.QA from Table 2; Fig-
ure 9 redraws that plane for En.QA, where the ef-
fect is sharpest, so the frontier can carry the claim
14
