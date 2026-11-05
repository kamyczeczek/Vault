---
type: Concept
id: 09_from_plan_to_action_how_well_do_agents_follow_th
title: "From Plan to Action: How Well Do Agents Follow the Plan? (part 10/13)"
source: "From Plan to Action How Well Do Agents Follow the Plan"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

From Plan to Action: How Well Do Agents Follow the Plan? ASE ’26, October 12–16, 2026, Munich, GermanyRegression
Summary
Devstral-small GPT5-mini DeepSeek-V3 DeepSeek-R1
Figure 10: Phase flow analysis under Regression Testing (L★(Φ)= 𝑅𝐺 N R P V 𝑉𝐺 ) and Summary plan setting (L★(Φ)=
N R P V S ).
(a) (b)
Figure 11: Impact of Regression Testing (a) and Summary plan (b) on the success rate.
Figure 12: Regression Testing plan compliance metrics.
Figure 13: Summary plan compliance metrics.
leads to moderately reduced success rates for Devstral-small, which
consistently relies on reproduction, and GPT-5 mini, which adap-
tively incorporates reproduction as problem difficulty increases.
Finding 11. Agents prioritize effective workflows over pre-
scribed phase ordering.Agents do not rigidly follow suboptimal
ordering constraints; instead, they override them in favor of execu-
tion orders that better support their problem-solving process.
Finding 12. Delaying weakly internalized phases can reduce
interference, but it does not consistently improve perfor-
mance.For models that do not naturally rely on a phase (e.g.,
Reproduction in DeepSeek-V3), postponing it can reduce interfer-
ence with early steps. However, this benefit is not consistent: after
accounting for nondeterminism (§6.2), the reordered plan yields
only a negligible change in success rate (38.3% to 38%).
5.3.2 RQ5.2. Reminded Plan Setting.To mitigate the context win-
dow pressure (§4.1.1), where the initial plan becomes less influential
as the trajectory length increases, we introduce a Reminded plan
setting. In this variant, the Standard plan is periodically re-inserted
into the context everyfivesteps. Figure 17 shows that periodic plan
reminders improve plan compliance for DeepSeek-V3 and maintain
similar𝑃𝐶 for the other models. This leads to consistent improve-
ments in success rates across models, as shown in Figure 15b. The
reminders prevent drifting into irrelevant sub-goals (e.g., exploring
unrelated directories) and return focus to the repair task.
6 Factors Beyond the Scaffold and LLM
6.1 RQ6. Generalization to Other Benchmarks
In previous RQs, we observed that plan variants affect model per-
formance and plan compliance differently, largely due to their in-
ternalized problem-solving strategies. One potential explanation is
data contamination, where models may overfit to the SWE-bench
Verified dataset. To assess generalization of the findings, we re-
peated RQ1–RQ5 on SWE-bench Pro [8], which aims to minimize
overlap with LLM training corpora through licensing constraints.
To minimize moving factors, we focused on 266 Python instances
of SWE-bench Pro. This benchmark is more challenging and less
contaminated, and the studied models achieve near-zero success
