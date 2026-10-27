---
type: Concept
id: 13_interpretable_context_methodology_folder_structu
title: "Interpretable Context Methodology: Folder Structure as Agent (part 14/21)"
source: "Interpretable Context Methodology Folder Structure as Agent.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, interpretable-context]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

14•Jake Van Clief, David McDermott
5 Discussion
5.1 Where This Works
ICM handles sequential multi-step workflows where a human reviews output at each stage. In practice, the
protocol has been applied to content production pipelines (script-to-animation, short-form video), training material
development (slide deck generation from source material), academic research workflows (at the University of
Edinburgh and ICR Research), and policy analysis (at the Academy of International Affairs, Bonn). The common
thread across these deployments is that the workflows are sequential, the outputs benefit from human review at
each step, and the same pipeline runs repeatedly with different input.
The common thread is that these workflows are sequential (step 2 follows step 1), reviewable (a human should
check each step’s output), and repeatable (the same pipeline runs weekly or daily with different input). For this
class of workflow, ICM provides full orchestration capability with no framework code, no server infrastructure,
and no developer dependency for day-to-day operation.
5.2 Where This Does Not Work
ICM is not a replacement for multi-agent frameworks in every context.
Real-time multi-agent collaboration, where agents need to communicate dynamically and respond to each
other’s outputs in tight loops, requires the kind of message-passing infrastructure that AutoGen [20] and similar
frameworks provide. ICM’s sequential, file-based handoffs are too slow for this.
High-concurrency systems where many users hit the same pipeline simultaneously need proper queueing,
state isolation, and deployment infrastructure. ICM is local-first by design. Scaling it to concurrent users would
require building the infrastructure ICM was designed to avoid.
Workflows that require complex branching logic based on AI decisions mid-pipeline are awkward in ICM. A
human can make branching decisions between stages (run stage 3a instead of 3b based on what they see in the
stage 2 output), but automated branching would require scripting that moves ICM toward being a framework
itself.
These boundaries matter. The claim is not that ICM replaces existing tools across the board. The claim is that
for a large and common class of workflows, the existing tools provide more complexity than the problem requires,
and that complexity has real costs: opacity, fragility, developer dependency, and overhead that slows iteration.
5.3 Observability as a Side Effect
The most useful property of ICM may be one that was not designed as a feature. Because every intermediate
output is a plain file, the system is observable by default. There is no logging layer to build, no dashboard to
configure, no special tooling to inspect pipeline state. You open a folder and read the files.
Rudin argued that inherently interpretable systems should be preferred over post-hoc explanations of opaque
ones [45]. ICM is a glass-box AI workflow. It did not become transparent through the addition of an explanation
layer. It was never opaque in the first place, because every artifact is a plain-text file that a human can read.
Amershi et al. ’s guidelines for human-AI interaction include “make clear what the system can do, ” “support
efficient correction, ” and “support efficient dismissal” [47]. Stage contracts make capabilities explicit. Markdown
files support efficient correction (open, edit, save). Review gates at every stage boundary support dismissal (decide
not to proceed, re-run the previous stage with different input, or abandon the run entirely).
The regulatory landscape may also be relevant here. The EU AI Act’s human oversight requirements [49, 50]
emphasize staged review, audit trails, and defined intervention points. ICM produces these as a byproduct of
its architecture: there is no way to run an ICM pipeline without generating inspectable intermediate artifacts,
because the intermediate artifacts are how the stages communicate. Whether this constitutes compliance with
