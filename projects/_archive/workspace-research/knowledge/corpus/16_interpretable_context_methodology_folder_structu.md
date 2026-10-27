---
type: Concept
id: 16_interpretable_context_methodology_folder_structu
title: "Interpretable Context Methodology: Folder Structure as Agent (part 17/21)"
source: "Interpretable Context Methodology Folder Structure as Agent.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, interpretable-context]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Interpretable Context Methodology: Folder Structure as Agent Architecture•17
The question is what a debugger for semantic content would look like. Several directions are worth exploring.
Output provenance through identifiers.If each section of a stage’s output carried an identifier linking it to
the source instruction or reference file that produced it, a practitioner could trace backward from any part of
the output to the context that generated it. In compiler terms, this is the equivalent of debug symbols or source
maps: metadata that connects output back to source without changing the output itself. In practice, this could
mean embedding lightweight markers (GUIDs, section tags, or comment annotations) in stage output files that
reference specific sections of the stage’sCONTEXT.mdor Layer 3 reference files.
Cross-stage trace verification.In the script-to-animation workspace described in Section 4, one recurring
problem has been misalignment between the animation specification (stage 3 output) and the script (stage 2
output). Timing drifts. Animations reference phrases that were revised. Visual density does not match pacing.
This is the source of the U-shaped intervention pattern observed in Section 4.4: the stage 3 editing that brings
intervention back up is almost entirely alignment work, tracing the final output back through the pipeline to find
where it diverged from earlier decisions. The current solution is an audit file that forces the agent to trace back
from the specification to the original script, re-verifying timing for each phrase and flagging inconsistencies.
This works well enough that it catches most alignment errors, and the errors it catches are remarkably consistent
in kind: frame count discrepancies, visual density mismatches, and pacing breaks at scene boundaries.
This audit file is a proto-debugger. It implements a specific kind of cross-stage verification: checking that the
output of stage 𝑛 is consistent with the output of stage 𝑛− 2by re-reading both and comparing them against
defined criteria. The pattern could be generalized. A stage contract could include a Verify section alongside its
Inputs, Process, and Outputs sections, specifying which earlier stage outputs should be checked for consistency
and what criteria to check against. The agent would run these verification checks as part of the stage’s execution
and flag discrepancies before the human reviews.
Breakpoints in markdown.The most speculative direction involves something like breakpoints for mark-
down files. In a traditional debugger, a breakpoint says “pause here and let me inspect the state. ” In ICM, a
breakpoint in a CONTEXT.md file might say “after the agent processes this instruction, show me what it produced
before continuing. ” This would be particularly useful in stages with complex instructions where the practitioner
wants to verify that the agent interpreted a specific constraint correctly before it finishes the rest of the stage’s
work. It turns a single-pass stage into a sequence of verifiable sub-steps.
These ideas are not yet implemented. They are described here because the gap they address, the ability to trace
output back to source, is a gap that compiler engineering solved decades ago and that ICM will need to solve as
workspaces grow more complex.
6.3 Source Integrity and the Edit-Source Principle
The current paper describes ICM’s review gates as places where practitioners edit stage output. This is useful
and it works. But there is an argument, drawn directly from software engineering practice, that the source files
should be what improves over time, and that editing output is treating symptoms rather than causes.
The argument is straightforward. If a script sounds wrong at stage 2, there are two possible responses. The
first is to edit the script directly: fix the tone, adjust the phrasing, move on. The second is to ask why the script
sounds wrong and trace the problem back to the source that produced it. Maybe the voice guide in the reference
material is underspecified. Maybe the stage contract’s instructions emphasize the wrong quality. Maybe the
research output from stage 1 framed the topic in a way that led the script in the wrong direction. Editing the
output fixes this run. Editing the source fixes every future run.
In compiler terms, editing the output is patching the binary. It works, but it does not improve the compiler. A
developer who finds a bug in compiled code traces it back to the source and fixes it there, so that every subsequent
build is correct.
