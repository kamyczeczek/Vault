---
type: Concept
id: 03_from_plan_to_action_how_well_do_agents_follow_th
title: "From Plan to Action: How Well Do Agents Follow the Plan? (part 4/13)"
source: "From Plan to Action How Well Do Agents Follow the Plan"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

dates.py
<old_str5, new_str6>str_replace  ✔
5
create test_ﬁx.py
python test_ﬁx.py
6
7
8
9
10
11
submit
1 view /testbed
2 view /testbed/django/contrib/auth
3 view /testbed/django/contrib/auth/token.py
str_replace token.py str_1 str_2
observation: Edit succeeds
4
submit5
/testbedview
/testbed/django/
contrib/authview
/testbed/django/co
ntrib/auth/token.pyview
1
2
token.py
<old_str1, new_str2>str_replace  ✔
3
submit
4
Langutory: RRRRNNNPPVV(R4N3P2V2) Langutory: NNNP(N3P)
PPC=1, POC=0.75, PPF=1
PC=0.91
PPC=0.5, POC=0.5, PPF=1
PC=0.63
(c) (DSK-V3 · django-13551 · Unresolved)(b) (DSK-R1 · matplotlib-21568 · Unresolved)
test_min_count_comprehensive.py
reproduce_bug.py
Figure 1: Illustrative examples of agent trajectories and their correspondingGraphectoryandLangutoryrepresentations.
Plan:L ★(Φ)= N R P V .
To illustrate the concept, Figure 1 shows three trajectories gener-
ated by SWE-agent along with their correspondingGraphectory
andLangutory. Figure 1a shows acompliantandsuccessfulex-
ecution.SWE-agent DSK-R1 starts by navigating to the buggy file
nanops.py (step 1), creates and executes a reproducing test (steps
2–3), edits the buggy file (step 4), validates the patch by creating and
executing a more comprehensive test (steps 5–7), edits the file again
to handle corner cases (step 8), and re-executes the test (step 9) be-
fore submitting the patch. This yields aLangutoryof 𝑁𝑅 2𝑃𝑉3𝑃𝑉 ,
which is compliant with the instructed planL★(Φ)= N R P V .
The execution in Figure 1b covers all plan phases in its trajec-
tory, but violates the intended order, with excessive reproduc-
tion (steps 1–4) preceding navigation (steps 5–7) and leading to an
unresolvedpatch. The execution in Figure 1c skips key phases, tran-
sitioning directly from navigation (steps 1–3) to patching (step 4)
before submission, violating the plan. The consequence of plan
violation is a low-quality patch that does not resolve the issue.
We will explain our novel process-centric plan compliance
metrics using this illustrative example. 𝑃𝑃𝐶 measures whether
LangutoryL(𝑇,Φ)covers the phases specified in the plan:
𝑃𝑃𝐶= |Φ∩{L(𝑇,Φ) 𝑡|1≤𝑡≤𝑛} |
|Φ| (1)
Here,L(𝑇,Φ) 𝑡 denotes the phase label assigned to the t-th action
in trajectory𝑇 under the phase vocabulary Φ.𝑃𝑃𝐶= 1if every
phase in Φ appears at least once in theLangutory. In practice,
an agent may skip some plan phases, e.g., directly jumping into
patching after navigation without reproduction test generation.
Therefore,𝑃𝑃𝐶∈[ 0, 1]. In Figure 1c, the agent skips reproduction
and validation, resulting in𝑃𝑃𝐶= 0.5. The executions in Figure 1a
and 1b cover all plan phases inΦand achieve𝑃𝑃𝐶=1.
Not only is covering all phases important, but so is following
the proper order through trajectory execution.𝑃𝑂𝐶 measures the
fraction of phases inL★(Φ) that appear in the correct relative order:
𝑃𝑂𝐶= LIS(𝑖 1,...,𝑖 𝑚)
𝑚 (2)
where LIS(·) denotes the length of the longest increasing subse-
quence and 𝑖𝑘 denotes the first occurrence index of phase 𝑝𝑘 in
L(𝑇,Φ) (if present). Phase revisits are allowed;𝑃𝑂𝐶 evaluates the
order of first occurrences. In Figure 1b, the first occurrence indices
of N R P V are[5, 1, 8, 10]. The longest increasing subsequence
is[1, 8, 10] with length3, yielding 𝑃𝑂𝐶= 3
4 . Failing to follow the
expected order can cause inefficient trajectories or task failure.
In Figure 1b, the agent begins with reproduction before properly
navigating the codebase, leading to repeated modifications to the
reproduction script (steps 3–4), and a failed edit at step 8.
Agents operate through iterative reasoning–action–observation
cycles [39], in which decisions arelocallyconditioned on the current
context rather than the initial instructed plan. Moreover, training
strategies can overfit the LLMs to certain actions outside of the
instructed plans for specific tasks. Hence, some actions may not
map to plan phases in theLangutory. For example, an agent may
decide to open a pull request after patch validation, which is not
part of the instructed plan in existing programming agents [1, 28,
34]. In such a case,Langutorymay containunknownletters that
are considered gibberish with respect to the specified plan phases.
Including additional actions beyond those in the recommended
plan is not necessarily negative, but can be distracting. Therefore,
𝑃𝑃𝐹 penalizes the appearance of phases outside the plan alphabet:
𝑃𝑃𝐹= |Φ|
|Φ∪{L(𝑇,Φ) 𝑡|1≤𝑡≤𝑛} | (3)
𝑃𝑃𝐹∈ ( 0, 1], and 𝑃𝑃𝐹= 1if every phase appearing in the
Langutorybelongs to Φ. The overall compliance score is the geo-
metric mean of its three component metrics:
𝑃𝐶=(𝑃𝑃𝐶 .𝑃𝑂𝐶 .𝑃𝑃𝐹) 1/3 (4)
𝑃𝐶∈[ 0, 1], where score𝑃𝐶= 1indicates perfect plan compliance.
Geometric mean aggregates sub-metrics multiplicatively, ensuring
equal weighting and preventing compensation across dimensions.
Low compliance in any dimension proportionally reduces the over-
all score. Lower 𝑃𝐶 scores reflect deviations in missing phases,
spurious phases, or violations of the logical phase ordering.
3 Empirical Setup
Models and Scaffold.To capture a multi-dimensional analy-
sis of plan compliance, we evaluate the SWE-agent scaffold [ 38]
across four diverse LLMs:GPT-5 mini[ 26] (closed-source fron-
tier reasoning model),DeepSeek-R1[ 7] (open-source reasoning
