---
type: Concept
id: 00_is_progressive_disclosure_all_you_need_for_long
title: "Is Progressive Disclosure All You Need for Long-Context Agents? (part 1/17)"
source: "Is Progressive Disclosure All You Need for Long-Context Agents"
tags: [agentic, agents, anti-leakage, context-engineering, icm, memory, planning, prompt-engineering, reflection, progressive-disclosure]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Is Progressive Disclosure All You Need for Long-Context Agents?
Yifeng He1, Yinzhe Zhao 2*, Jicheng Wang 1, Hao Chen 3
1University of California, Davis
2Zhejiang University, 3The University of Hong Kong
yfhe.cs@gmail.com, chenho@hku.hk
Abstract
Long-document question answering usually
forces a choice between loading the whole doc-
ument into the context window and bolting
on a separate retriever. Agentic AI suggests
a broader option, giving the agent the docu-
ment path and letting it decide how and what to
read. Agent Skills, a standard for packaging ex-
pertise into folders an agent loads on demand,
supply a ready mechanism:progressive disclo-
sure, which exposes only what a query needs,
from a short description down to the specific
passages. Practitioners rapidly adopted this pat-
tern for book-length understanding tasks, but
the evidence for it has been anecdotal. We run
the first controlled study of the pattern, com-
paring raw-document navigation and several
designs of Agent Skills packs against a clas-
sical hybrid retriever across three agent har-
nesses and three model families on ∞Bench.
On a single book, the gain depends on the har-
ness, running large when the agent navigates
the raw document poorly but near zero when a
strong agent harness already locates and reads
the right passages on its own. When scaling up
to tasks that span many books, raw-document
navigation collapses while one-level progres-
sive disclosure degrades more slowly and pulls
ahead. A second, deeper routing level never
helps and sometimes breaks accuracy outright,
so one level is enough. Progressive disclosure
buys context, not intelligence: it is redundant
while a strong agent can locate the right pas-
sages itself, and decisive once the corpus grows
too large to navigate by reading.
1 Introduction
Long-document question answering (QA) forces a
choice between two well-studied options: load the
entire document into the context window and lean
on the model’s long-context attention, or retrieve
a small set of chunks with an external retriever.
Neither option wins outright (Li et al., 2024, 2025),
*Work done while interning at UC Davis.
and on long inputs the effective context size falls
well short of the advertised window (Liu et al.,
2024; Hsieh et al., 2024). Agentic AI reframes
the choice: give the agent the document and let it
decide what to read and when. Claude Code made
exactly this move, dropping the retrieval index its
early versions used in favor of letting the agent
search the code base on demand (Cherny and Wu,
2025). But its engineers report the switch from
experience, not a controlled comparison.
Agent Skills turn that option into a mechanism.
The standard packages expertise as a directory of in-
structions and resources (Anthropic, 2025b; Xu and
Yan, 2026): root the document at aSKILL.md file,
hand it to the agent, and letprogressive disclosure
do the retriever’s job, keeping a short description
of each skill always in context so the agent reads
a skill’s body and its bundled files only when that
description matches the task. The pattern spread on
engineering intuition long before anyone measured
it (Hacker News, 2025a,b). For book-length mate-
rial, it is urged as a way to package a whole book
so that an agent reads only the chapter a question
needs (Virgilio Jr., 2026; Praison, 2026; PyShine,
2026). However, whether it should displace re-
trieval is itself contested (Ewerlöf, 2026), and no
controlled study has yet tested it with an agent on
a standardized long-document benchmark.
This practice raises two open empirical ques-
tions. First,does progressive disclosure work for
book-length understanding?Second,what is the
best way to structure the skill pack?Both are
sharper than they first appear, because the Agent
Skills specification bundles two design choices
the practitioner literature never separates: how
deep the disclosure recurses, and where the per-
chunk index physically lives. We pull them apart
by comparing the three approaches an agent can
take to a book-length document. Raw-document
navigation ( raw) gives the agent the document
with no skill pack. Flat disclosure ( flat, Fig-
1
arXiv:2607.17598v1  [cs.AI]  20 Jul 2026
