---
type: Concept
id: 11_interpretable_context_methodology_folder_structu
title: "Interpretable Context Methodology: Folder Structure as Agent (part 12/21)"
source: "Interpretable Context Methodology Folder Structure as Agent.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, interpretable-context]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

12•Jake Van Clief, David McDermott
Stage 1 output
(Research)
Stage 2 output
(Script)
Stage 3 output
(Production)
Never
Rarely
Sometimes
Often
Almost always 92%
30%
78%
Frequency of human edits
Fig. 5. Observed frequency of human edits at each stage boundary, reported by 33 practitioners using multi-stage ICM
workspaces. Intervention follows a U-shaped pattern: heavy at stage 1 (direction-setting), light at middle stages (constrained
execution), heavy again at the final stage (aligning output with earlier decisions). Stage 1 editing is creative judgment.
Final-stage editing is closer to debugging. Values are approximate and based on practitioner self-report through conversation,
not instrumented measurement.
least a preliminary answer: yes, across academic research, policy analysis, and content production. A structured
study of these external deployments is a clear next step.
4.5 Early Practitioner Experience
ICM has been used in production across content creation, training material development, research analysis, and
policy workflows. The observations reported here are drawn from an invite-only practitioner community of 52
members whose backgrounds range from AI engineers and software developers to business owners, content
creators, and academic researchers. These observations come from ongoing conversations with community
members rather than from formal data collection protocols. They should be read as practitioner reports rather
than controlled findings, but they reflect a broader base of experience than the author’s own use alone.
The most consistent observation is where people choose to intervene (Figure 5). Across 33 community members
who have used the script-to-animation workspace or structurally similar multi-stage workspaces, 30 report an
intervention pattern consistent with a U-shape: heavy editing at stage 1 (direction-setting), light editing at the
middle stages, and heavy editing again at the final stage (aligning output with earlier decisions). The remaining
three report roughly equal editing across all stages. These numbers come from practitioner conversations, not
from instrumented measurement, and should be interpreted accordingly.
The two peaks reflect different kinds of editing. Stage 1 editing is directional: the user is narrowing from broad
possibilities to a specific angle, deciding what the piece is about. This is creative judgment. Final-stage editing is
alignment work: the user is checking that the output faithfully represents decisions made in earlier stages. This is
closer to debugging. The practitioner traces a misalignment in the output back through the pipeline to find where
it diverged from the source material. Section 6 explores what tooling for this kind of traceability might look like.
The middle stages get the lightest touch because they sit between well-defined anchors. The earlier stage output
sets the direction. The reference material (Layer 3 voice guides, structural templates) constrains the execution.
With both anchors in place, the middle stages have less room to go wrong, and practitioners tend to trust them.
This aligns with Parasuraman, Sheridan, and Wickens’s observation that appropriate automation levels vary by
task function [42].
