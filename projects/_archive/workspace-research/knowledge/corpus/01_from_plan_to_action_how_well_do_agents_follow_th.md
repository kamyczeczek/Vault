---
type: Concept
id: 01_from_plan_to_action_how_well_do_agents_follow_th
title: "From Plan to Action: How Well Do Agents Follow the Plan? (part 2/13)"
source: "From Plan to Action How Well Do Agents Follow the Plan"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

ASE ’26, October 12–16, 2026, Munich, Germany Shuyang Liu, Saman Dehghan, Jatin Ganhotra, Martin Hirzel, and Reyhaneh Jabbarvand
• RQ1: Standard Plan Compliance (§4.1).To what extent do
agents follow the instructed plan? What factors impact plan
compliance and violations? Does plan compliance help agents
resolve issues?Findings.Agents follow the standard plan, al-
though with varying compliance rates. Some strictly follow the
plan in the specified order, while others adaptively override the
plan based on the trajectory, depending on the problem’s dif-
ficulty. Following the plan positively helps all agents resolve
more GitHub issues. The fine-tuning paradigm, context window
pressure, data contamination, overfitting, and optimization for
short-term reward are the most prevalent factors impacting plan
compliance.
• RQ2: Behavior of Agents in the Absence of Plan (§4.2).How
do agents operate in the absence of a plan? To what extent does re-
moving the plan impact overall performance?Findings.Without
a plan, agents follow their internalized problem-solving strategy,
which overlaps with the standard plan to a varying degree. The
success rate, however, drops in the absence of the standard plan.
• RQ3–RQ5: Impact of Plan Variations (§5.1–5.3).Do agents
heed removal, addition, and reordering of plan phases? To what
extent does frequent reminding of the plan phases help com-
pliance in the long-horizon task of program repair?Findings.
Removing a standard plan phase, even if the agent usually ig-
nores it under the standard plan setting, negatively impacts the
agents’ performance, confirming the overall impact of a global
plan on local reasoning steps. The negative impact of a bad plan
is greater than no plan at all. Surprisingly, augmenting plans with
task-relevant phases inspired by best practices also negatively
affects agents’ performance when they are not aligned with the
model’s internal strategy. Periodic plan reminders reduce plan
violations and improve performance.
• RQ6: Generalization to Other Benchmarks (§6.1).How much
can the observations and conclusions about plan compliance gen-
eralize to another benchmark, i.e., SWE-bench Pro [8]?Findings.
The plan compliance rate of the agents across all settings on SWE-
bench Pro drops by 13%, on average, compared to SWE-bench
Verified. The agents exhibit different phase flow patterns, e.g.,
they give up on generating reproduction tests early and validate
patches using existing regression tests rather than generating
tests. This is likely because SWE-bench Pro instances are more
challenging and less contaminated, and the high-level standard
plan is no longer effective at guiding the agents.
• RQ7: Impact of Nondeterminism (§6.2).To what extent is
plan compliance of agents under different plan settings attributed
to nondeterminism?Findings.Nondeterminism exists but does
not impact our findings. We account for nondeterminism by
repeating experiments and comparing persistent behaviors across
plan settings.
We are thefirstto (1) conduct a large-scale analysis of plan
compliance by agents, (2) introduce novel plan compliance metrics,
(3) speculate the root causes of plan violations, and (4) study how
plan compliance relates to task success. Our findings suggest that
the effectiveness of the plan is tightly coupled to its alignment
with the model’s internalized workflow and the task’s complexity.
Therefore, future research should focus on fine-tuning paradigms
that teach models to follow plans more effectively, rather than
encoding task-specific plans into them.
2 Experimental Design
We aim to analyze whether and to what extent programming agents
follow the specified, task-appropriate software engineering work-
flows. Given the popularity of programming agents for fixing real-
world GitHub issues, this study will focus on program repair. The
default practical workflow for this task involves localizing the bug,
patching the code, and then validating whether the patch resolved
the bug. Many existing scaffolds, e.g., SWE-agent/mini-SWE-agent,
Trae agent, and OpenHands,explicitly instructthe agent to follow
a similar plan in their system prompt1 [1, 28, 34]:
• Navigation (N). The agent searches for, opens, and reads files
relevant to the issue description, building an understanding of
the codebase and localizing the relevant components.
• Reproduction (R). The agent generatesnew teststo reproduce
the bug, i.e., tests that fail on the buggy code.
•Patch (P). The agent edits the application code to fix the bug.
• Validation (V). The agent runsreproduction testsand generates
new tests to validate patch correctness.
Assessing whether an agent follows the instructed plan
for a task requiresprocess-centricanalysis of trajectories. We
build our process-centric analysis on top ofGraphectoryand
Langutory[ 21].Graphectoryrepresents linear raw trajecto-
ries as enriched graph structures, where nodes are the agent’s
distinct actions and edges denote the chronological execution order.
Langutoryis an abstract representation of the trajectory in the
form of language. That is, by mapping the agent’s actions across
the sequence of𝑛 trajectory steps𝑇=(𝑠 1,...,𝑠 𝑛) to an alphabet
Φ={𝑝 1,...,𝑝 𝑚} of𝑚 letters2,Langutory L(𝑇,Φ) explains the
agent’s problem-solving strategy as a sequence of letters.
When the alphabet denotes plan phases, constructing
Langutoryrequires mapping each raw trajectory action to the
phase it attempts to perform. We map file and directory inspection
to Navigation, newly generated test creation and execution before
any application-code edit to Reproduction, application-code edits
to Patch, and newly generated test creation or execution after
patching to Validation. Agent-generated tests are distinguished
from existing repository tests: running existing tests is treated
as regression testing, which is outside the default NRPV plan
unless explicitly included in a plan variant. Actions that do not
correspond to a plan phase, such as environment probing or
dependency checks, are labeled as General. For dynamically
executed Python code, such as heredocs, we parse the code to
identify environment setup, file modifications, and test logic using
signals such as assertions and test-specific imports (e.g., pytest,
unittest, and mock). The mapping implementation is available in
our artifact [22].
Given a plan phase alphabet Φ and expected phase sequence
L★(Φ), we say aLangutorycomplieswith the instructed plan if it
includes all and only specified plan phases in the specified order.
We propose a novel process-centric metric,plan compliance( 𝑃𝐶),
measured across three dimensions:plan phase compliance( 𝑃𝑃𝐶 ),
plan order compliance(𝑃𝑂𝐶), andplan phase fidelity(𝑃𝑃𝐹).
1The specified plan for some agents could be more verbose. Regardless, all existing
agents follow similar high-level plans.
2𝑚≪𝑛to show an overall strategy rather than detailed actions.
