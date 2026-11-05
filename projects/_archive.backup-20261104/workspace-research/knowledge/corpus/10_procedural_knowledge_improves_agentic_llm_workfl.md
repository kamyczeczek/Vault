---
type: Concept
id: 10_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 11/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

in task success rate than the LLM system without a task planner. This is true in both domains for
GPT-oss-120b, but the results for GPT-oss-20b show less improvement; we hypothesize that smaller
models such as GPT-oss-20b can run into context length issues that are not addressed by our task
network approach. We further examine several more questions about these results.
Why is No-TN doing so poorly?Although not obvious from the results presented so far, there are some
subtle differences in model behavior that we would like to discuss. To explain, consider the first few
steps that an LLM may need to take to solve one of the agentic problems seen so far. In each of the
problems, there is a request.txt and a problem specification.txt. The first few steps of solving an
agentic task is to read each of these files and then take notes on the files into the short-term memory file
(Notes). Some models (e.g., nemotron, codestral, llama) are naturally proficient in this and will generate
a sequence of actions:
1. Readrequest.txt
2. Append [request details]
3. Readproblem specification.txt
4. Append [spec details]
This sequence of actions can be generated even if the task network does not have explicit task nodes
about taking notes (or even without a task network at all). However, our experiments with GPT-oss-120b
revealed the system would get stuck in loops like:
1. Readrequest.txt
2. Readproblem specification.txt
3. Readrequest.txt
4. Readproblem specification.txt
5. etc.
This causes the system to timeout and fail as a result. We can alleviate this problem for domains such
as BW by explicitly extending the final goal for the task. For example, we could change solve the user
request into solve the user request and have notes on the request and problem specification. But
such
changes may not scale if a problem has many goals.
Are LLM-constructed task networks better? (LLM-TN)To study LLM-TN, we constructed a prompt
that includes the problem specification, the agent prompt, and two valid task network node examples
and asked Gemini 2.5 Pro to produce a task network (LLM-TN). In Figure 3, we see that task success
rate ofLLM-TN(brown bars) does better thanNo-TNwhile varying againstHuman-TN.
Does Human-TN or LLM-TN save runtime?Figure 4 shows runtime statistics for GPT-oss-120b in
ProcLLM across the evaluation benchmarks (Figure A.2 shows full details). For Blocks World and Unit
Movement, the statistics are averaged over all problem sizes.
In three of the four benchmarks, the task planner decreases the number of system iterations required
for a given problem instance. The exception is Recipe Generator, where the LLM withNo-TN produces
quick but always incorrect outputs, unlike other benchmarks where No-TN typically fails via timeout.
One explanation is that the LLM can treat the request in Recipe Generator as a query to be answered
directly, bypassing the APIs altogether. This shortcutting behavior mirrors earlier findings (( 3)) that
LLMs can default to superficial strategies unless constrained externally.
Using a task network typically increases the average time per iteration while decreasing the total
number of iterations. One important takeaway is that using the task network does not significantly
increase the time it takes to complete a task. In some cases, such as on BlocksWorld, using GPT-oss-20b
in ProcLLM will outcompete GPT-oss-120b in both time and performance metrics.
7 Conclusion
We have argued that procedural knowledge helps LLM workflows. We formalized, implemented, and
evaluated ProcLLM that uses HTNs to improve LLM performance on complex agentic tasks. ProcLLM
leveraged an HTN to decompose complex tasks into subtasks that completed by an agentic LLM. While
12
