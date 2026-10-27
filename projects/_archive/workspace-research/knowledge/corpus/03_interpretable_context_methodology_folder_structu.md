---
type: Concept
id: 03_interpretable_context_methodology_folder_structu
title: "Interpretable Context Methodology: Folder Structure as Agent (part 4/21)"
source: "Interpretable Context Methodology Folder Structure as Agent.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, interpretable-context]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

4•Jake Van Clief, David McDermott
This matters because of how language models handle context. Liu et al. demonstrated that LLMs perform
significantly worse when relevant information is buried in the middle of long contexts [25]. The more irrelevant
material in the context window, the worse the model performs on the material that matters. Jiang et al. showed
that prompt compression can achieve up to 20x token reduction with minimal performance loss [31], but a simpler
approach is to avoid loading irrelevant context in the first place. Stage-specific context loading, where each stage
only sees the files it needs, prevents the problem rather than treating it after the fact.
It is worth distinguishing ICM from Anthropic’s Model Context Protocol (MCP) [23]. MCP standardizes how
models access external tools and data sources, solving the integration problem between AI systems and the
services they need to call. ICM addresses a different layer: how to structure and deliver context to an agent
across a multi-stage workflow. The two are complementary. An ICM stage might use MCP connections to access
external services, while the stage’s folder structure determines what context the agent receives when doing
so. This separation matters for efficiency as well. Jones and Kelly at Anthropic observed that loading all tool
definitions upfront into the context window slows agents and increases costs [24]. ICM’s stage-based architecture
avoids this by scoping tool definitions to individual stages, loading only the tools relevant to the current step.
2.3 Human Oversight and Observability
The question of how humans should relate to automated systems has been studied for decades, and the findings
are remarkably consistent.
Fails and Olsen introduced the interactive machine learning paradigm in 2003: rapid cycles of system output,
human feedback, and correction [35]. Amershi et al. argued that interactive ML must involve users at all stages,
from training through evaluation, with interfaces that support steering and correction [34]. Dudley and Kristens-
son’s review of interface design for interactive ML emphasized that transparent, inspectable representations are
essential for effective human-AI collaboration [36].
Eric Horvitz’s work on mixed-initiative systems established principles for coupling automated services with
human control [37]. The key insight: systems should let users invoke, adjust, and terminate automated processes
at natural breakpoints. This requires that the system’s state be visible and its actions be reversible.
Parasuraman and Riley identified the failure modes that emerge when this goes wrong [41]. When automated
outputs are opaque, people either trust them blindly (misuse) or stop using them entirely (disuse). Both failures
stem from the same cause: the human cannot see what happened between input and output. Lee and See’s
work on trust calibration reinforced this: appropriate trust requires that system behavior be observable [ 40].
Parasuraman, Sheridan, and Wickens proposed a taxonomy of automation levels, noting that the right level of
automation varies by task and that systems should support different levels at different stages [42].
Ben Shneiderman synthesized these threads into the Human-Centered AI framework, arguing that systems
can achieve both high human control and high automation simultaneously [43]. The two are not in tension. They
reinforce each other when the system is designed to be comprehensible, predictable, and controllable [44].
Cynthia Rudin made the most forceful version of this argument: stop building opaque systems and then trying
to explain them after the fact. Build systems that are inherently interpretable [45]. This applies at the workflow
level as much as at the model level. A production pipeline where every intermediate output is a readable file is
inherently interpretable. There is nothing to explain because nothing was hidden.
This is also becoming a regulatory concern. The EU AI Act requires human oversight of high-risk AI systems,
distinguishing between human-in-the-loop, human-on-the-loop, and human-in-command approaches [49]. Nov-
elli et al. argue that effective oversight requires institutional design, not just technical capability [50]. Systems
with staged review points, audit trails, and defined intervention surfaces have a practical advantage as these
requirements take effect.
