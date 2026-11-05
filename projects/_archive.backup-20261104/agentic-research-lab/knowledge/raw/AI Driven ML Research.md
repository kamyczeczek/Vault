---
type: Concept
title: "AI-Driven Machine Learning Research via Interpretable Context Methodology"
source: "https://arxiv.org/abs/2603.16021"
tags: [icm, interpretable-context-methodology, ml-research, multi-agent, staged-workflow, scientific-workflow, research-automation]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

AI Driven ML Research

This is a follow-up to my previous post about using ICM for AI-driven machine learning research. In one week of ICM-assisted research, I've moved further than I managed in roughly six months of my master's thesis.

This is what that looks like in practice:
ICM/

├── README.md

├── skills/

├── agents/

│ ├── literature-intake.md

│ ├── research-development.md

│ ├── code-development.md

│ ├── results-evidence.md

│ ├── research-argument.md

│ ├── thesis argument.md

│ ├── self-review.md

│ └── ...

├── research/

│ ├── context/

│ ├── literature/

│ ├── development/

│ ├── results/

│ └── reports/

├── code/

│ ├── src/

│ ├── tests/

│ └── runs/

├── thesis/

└── _system/

├── rules/

├── templates/

└── schema/

I can queue several research goals across different chats and let each one keep moving. The agents are not all doing the same job with different names. Each one has a bounded responsibility, its own context and a clear handoff to the next part of the work.

- The literature-intake agent turns papers into usable research context. It extracts the claims, methods, datasets, assumptions and limitations that matter for my problem. It helps answer: what has already been tried, what can actually be reused and what still needs to be tested?

- The research-development agent turns vague ideas into explicit questions, hypotheses and experiments. It forces the research to become testable before implementation begins. Instead of “try an LSTM”, the goal becomes something like: under these conditions, does recursive probabilistic prediction outperform a defined baseline?

- The code-development agent owns the implementation. It builds the data pipeline, model interfaces and experiment code while respecting the assumptions defined by the research question. Its job is not to decide whether the research is meaningful. Its job is to make the proposed experiment executable and reproducible.

- The testing agent checks whether the implementation behaves as intended. It verifies data shapes, transformations, edge cases, saved artifacts and the parts of the pipeline that can be checked mechanically. A passing test gives me confidence in the software. It does not give me scientific confidence in the conclusion.

- The results-and-evidence agent turns runs into inspectable evidence. It collects metrics, compares baselines, generates visualisations and records what actually happened. It can show that one model performed better, but it must keep that observation separate from an explanation of why.

- The research-argument agent connects evidence to the argument. It asks whether the conclusion is supported, whether an alternative explanation is possible and which limitations need to be stated. This is where a collection of results starts becoming a defensible research story.

- The self-review agent looks for gaps across the whole chain: missing baselines, unsupported claims, weak tests, unclear assumptions, undocumented decisions or conclusions that go beyond the evidence.

I can move between these agents while each thread keeps its own objective, context and next step. They are not replacing one researcher with seven autonomous researchers. They are giving one research process several specialized working surfaces.

That changes the shape of research.

I'm no longer forced to finish one task completely before starting the next. I can keep several connected loops alive at the same time:

question -> hypothesis -> experiment -> evidence -> interpretation -> next question

- One agent can formulate the experiment. The context connects the work, while the boundaries stop every agent from pretending it owns the entire research process.

- A test can show that the implementation works. It cannot prove that the model is useful. A result can show that one approach performed better. It cannot automatically explain why. A paper can inspire an architecture. It cannot validate that architecture on my dataset.

- The human still provides the judgment, curiosity and scientific direction. ICM provides structure, memory, continuity and execution.

ICM gives these different kinds of work a connected, reviewable place. It keeps the reasoning, decisions, evidence and limitations attached to the research instead of scattering them across disconnected sessions. And the system itself is becoming part of the research.

My research template keeps growing. It captures the workflow, helps agents follow it, reviews what happened and suggests how the template can improve. It is becoming less like a static prompt and more like a reusable research environment with its own feedback loop.

That's why this feels so transformative for ML research.

- Not because the AI replaces the researcher.
- But because it lets the researcher keep more good questions moving at once.

I'm spending less time wrestling with the machinery around research - and more time deciding what is worth investigating next.

And the funny thing is: I'm only getting started.

19



5 comments



Leo Saraiva

• 22h

Seven agents is easy to say and hard to keep honest, and the thing that usually rots first is not the agents, it is the handoff. What does one of yours have to leave behind before the next one is allowed to start, a file with a fixed shape, or prose the next one reads?

Asking because self-review is carrying a lot here. It can only find what got written down, so a decision made in a chat and never recorded is invisible to it by construction. Curious what it actually catches in practice. Mostly missing baselines, or mostly claims the evidence does not carry?

3

Reply



Maxwell Troy-O'Donovan

• 21h

[@Leo Saraiva](https://www.skool.com/@56c228d1ecde46ceb37916cdf6891ba2?g=cliefnotes)

 Interesting questions. Seems like AI still needs a human in the loop at certain points

3

Reply



Leo Saraiva

• 9h

[@Maxwell Troy-O'Donovan](https://www.skool.com/@9436fd7d390a43759a5c341c5b8be779?g=cliefnotes)

 I would push back on that a little. It is less that a human has to be watching at certain points, and more that some calls cannot be checked from inside the folder at all. Whether a baseline is a fair comparison is not a fact sitting in the files, so more review does not find it.

What helped me was writing down which decisions are unfalsifiable from the inside. That list stays short, and it is the only place a person is genuinely required rather than just reassuring.

1

Reply



Maxwell Troy-O'Donovan

• 30m

[@Leo Saraiva](https://www.skool.com/@56c228d1ecde46ceb37916cdf6891ba2?g=cliefnotes)

 Appreciate you sharing, I don't have enough knowledge of ICM yet but it seems to make a lot of sense

0

Reply



Luis Velasquez

• 18h (edited)

This is wild. Super cool to see the use case. Curious how your work is connected to this, meaning are they similar concepts or different.

https://github.com/jmiao24/Paper2Agent