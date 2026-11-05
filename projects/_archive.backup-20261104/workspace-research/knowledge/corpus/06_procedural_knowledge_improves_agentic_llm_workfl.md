---
type: Concept
id: 06_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 7/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

with the following text (.txt) files or python (.py) code, where the first column rwa indicates allowed
read/write/append actions, respectively.
r ProblemSpec outlines the domain-specific rules of the problem to solve and format ofAnswer, which
is the same for all request instances. (See §C for full details.)
r Request contains problem instance details to be solved such as the initial configuration of the
problem and the goal configuration. (See §C for full details.)
r ToolsSpec is a human readable description of Tools, which are APIs that include source code,
informational text files, or structured text (e.g., csv, JSON).
rwa Notes starts empty and will contain the agent’s progress or details about the task or task history.
rwa Solver is only provided for some problems; the environment executes it, writing to output and error.
rwa Answer starts empty and will contain the agent’s solution to the overall task.
The content of the files as well as other details are assembled into context C=A(e 1, e2, ..., ek) containing
one or more elements ei. For ProcLLM this includes the action context Ca =A a(s,trace, κ)), and the
verify contextC v =A v(s,trace, κ).
Algorithm 1A general procedure for ProcLLM.
Input:Task SequenceK, MethodsM, horizonH
1:procedureProcLLM(K,M,H)
2: UpdateTask (K,M)
3:foriin1, ..., Hdo
4:ifK==∅thenbreak
5:κ←head(K)
6:C a ←A a(s,trace, κ)
7:a(params)←action-LLM(C a)
8:trace←‘’
9:ifa=verifythen
10:C v ←A v(s,κ)
11:verified,feedback←verify-LLM(C v)
12:trace←feedback
13:ifverifiedthen
14:pop(K)▷remove first taskκfromK
15: UpdateTask (K,M)
16:else▷apply r/w/a to env’t; (performss ′ ← T(s,a))
17:trace←file▷write file to the trace
18:ifa=write(file, content)thenfile.clear()
19: file←file + content
20:iffile=Solver then
21: out, err←Exec(Solver )
22:trace←trace+out+err
23:procedureUpdateTask(K,M)
24:m←FindFirstRelevantMethod(head(K),M)
25:ifmthen
26:push(m.subtasks, K)▷Prependm.subtasks
27: UpdateTask (K,M)▷Decompose further
ActionsAand transitionT. The agent can take one of four actions:verify,read,write, orappend.
The internal action verify calls a process that checks if the current task has been satisfied, returning a
boolean verified if the task is completed as well as feedback which is added to the trace. The verify
step is domain-specific and uses the verify-LLM. (A detailed example of theverify prompt is provided
in Appendix F.)
The external actions modify the writeable files, which are subsequently assembled into the context.
These include:
read(file ): copies file into Notes
write(file ,content): overwrites file withcontent
append(file ,content): appendscontentto file
These external actions must be in a JSON format for the environment to execute (for a detailed example,
7

Figure 2: System overview, labeled with components of the MDP . Blue boxes denote text files, orange
boxes denote LLMs, red boxes denote python files, and green boxes denote API files (scripts/databas-
es/etc.).
8
