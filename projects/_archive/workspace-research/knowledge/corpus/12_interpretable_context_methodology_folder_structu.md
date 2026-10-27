---
type: Concept
id: 12_interpretable_context_methodology_folder_structu
title: "Interpretable Context Methodology: Folder Structure as Agent (part 13/21)"
source: "Interpretable Context Methodology Folder Structure as Agent.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, interpretable-context]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Interpretable Context Methodology: Folder Structure as Agent Architecture•13
A second pattern involves prompt editing. Non-technical users, people without development experience, have
successfully modified stage behavior by editing the markdown CONTEXT.md files. Changes include adjusting tone
instructions, adding constraints (“keep scripts under 90 seconds”), and reordering the emphasis within a stage’s
process description. These edits would be equivalent to modifying agent configuration in a framework-based
system, a task that typically requires a developer. The plain-text interface lowers this barrier in practice.
A third pattern is worth noting for its implications about accessibility. Three community members with no prior
coding experience and no previous exposure to Claude Code used the ICM workspace-builder’s questionnaire
and setup process to create and run workspaces that produced ten-minute animated videos from scripts. They
edited CONTEXT.md files, reviewed stage outputs, and iterated on their workspaces without developer assistance.
This is a single data point from a small group, but it suggests that the filesystem interface can make AI agent
orchestration accessible to people who would not be able to use a framework-based system at all.
A fourth pattern is workspace duplication. Users who have a working workspace for one content format (say,
short explainer videos) duplicate the folder, modify the stage prompts to target a different format (say, long-form
essays), and run the new workspace without rebuilding from scratch. The workspace-builder supports creating
workspaces from nothing, but in practice people often prefer to copy and adapt an existing one. This mirrors
how Unix users build new shell scripts by modifying existing ones rather than starting from a blank file.
These observations are drawn from a community of varied backgrounds across a growing but still limited set
of workflow types. A structured evaluation with formal data collection, systematic interviews, and controlled
comparisons would be needed to draw firm conclusions about the generality of these patterns. The observations
are reported here because they informed the protocol’s design evolution and because they suggest directions for
future study.
4.6 Threats to Validity
Several limitations constrain the conclusions that can be drawn from the current work, and naming them is
important for interpreting the results above. The practitioner community provides a broader evidence base than
single-author observation, but data collection has been informal: observations come from ongoing conversations
rather than structured interviews, diary studies, or instrumented usage logging. The community is invite-only and
self-selected, introducing both selection bias and potential enthusiasm bias. The reported intervention patterns
(30 of 33 practitioners observing a U-shape) are self-reported through conversation and have not been verified
through controlled measurement.
While ICM has been adopted across content production, academic research, and policy analysis workflows, the
majority of active use remains concentrated in content production. The academic and policy deployments are
early-stage, and their outcomes cannot yet be reported in detail. All testing was conducted using a single model
family (Claude Opus 4.6 and Sonnet 4.6). Cross-model evaluation is a natural next step but falls outside the scope
of this paper, which focuses on the architectural pattern and its interaction properties rather than model-specific
performance. Output quality may vary with other models, particularly those with different context-handling
characteristics.
No controlled comparison has been conducted between ICM’s staged context loading and a monolithic
prompting approach on the same tasks, so the claim that scoped context improves output quality rests on
the theoretical support from the “lost in the middle” literature [ 25] and practitioner judgment rather than
measured effect sizes. A formal user study with systematic data collection, structured interviews, and controlled
comparisons across varied workflow types and participant backgrounds would substantially strengthen the
empirical foundations of this work.
