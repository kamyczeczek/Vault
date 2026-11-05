---
type: Concept
id: 07_interpretable_context_methodology_folder_structu
title: "Interpretable Context Methodology: Folder Structure as Agent (part 8/21)"
source: "Interpretable Context Methodology Folder Structure as Agent.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, interpretable-context]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

8•Jake Van Clief, David McDermott
Research Script Production Monolithic
0
0.5
1
1.5
2
3
4
5
·104
⁄tildelow42k
⁄tildelow5.6k⁄tildelow5.5k⁄tildelow4.9k
Tokens in context window
Layers 0–2 (structural) Layer 3 (reference) Layer 4 (working) Unused/irrelevant context
Fig. 3. Context window composition by stage (representative token counts from the script-to-animation workspace). The
three ICM stages each deliver 2,000–8,000 focused tokens. A monolithic approach loading all stages’ instructions, all reference
material, and all prior outputs produces a context window exceeding 40,000 tokens, most of it irrelevant to the current task.
their best. Figure 3 illustrates this composition across three example stages and contrasts it with a monolithic
approach.
Contrast this with a monolithic approach where all stage instructions, all reference files, and all prior outputs are
loaded into a single prompt. That approach can easily reach 30,000 to 50,000 tokens, pushing into the range where
Liu et al. found significant performance degradation on information retrieval tasks [25]. The “unused/irrelevant
context” segment in the monolithic bar of Figure 3 represents tokens from stages other than the one currently
executing: instructions the agent will not follow during this step, reference material that applies to a different
stage, and prior outputs already consumed by earlier stages. In ICM, these tokens are never loaded. In a monolithic
prompt, they occupy context space without contributing to the current task. The compression research by Jiang et
al. [31, 32] addresses this problem after the fact. ICM’s architecture avoids it by construction: each stage receives
a focused, appropriately sized context window because the folder structure determines what gets loaded.
Richard Gabriel argued that systems prioritizing simplicity of implementation over feature completeness tend
to survive and spread, because they are easier to port, easier to understand, and easier to improve incrementally
[11]. ICM trades the flexibility of a programmatic orchestrator for the portability, inspectability, and editability of
plain files. That tradeoff is the point.
In the same spirit, Plan 9 from Bell Labs extended Unix’s “everything is a file” principle to its full conclusion,
representing all system resources as files in per-process namespaces [ 12]. ICM applies the same idea to AI
workflows: all state, all context, all instructions exist as files in a folder namespace.
3.3 Stage Contracts and Handoffs
Figure 4 illustrates the flow between stages. Each stage reads from the previous stage’s output folder, processes it
according to its own contract, and writes to its own output folder. At each boundary, the human can inspect and
edit the output before the next stage runs.
