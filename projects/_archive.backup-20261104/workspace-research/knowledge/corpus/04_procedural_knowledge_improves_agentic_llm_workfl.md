---
type: Concept
id: 04_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 5/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

1{"m-travel-process-user-request": {
2"task": "process user request",
3"subtasks": {"1": "understand user request",
4"2": "choose a departing flight",
5"3": "choose a returning flight",
6"4": "choose an accommodation" },
7"verify": "answer.txt contains a solution in the correct format that follows the problem specification",
8"verify _files": {"file1": "problem_specification.txt",
9"file2": "answer.txt" }},
10"m-choose-departing-flight": {
11"task": "choose a departing flight",
12"subtasks": {"1": "understand flights tool",
13"2": "write flight to notes" },
14"verify": "notes contains details about a flight number and cost for a flight from origin to destination on departure
date consistent with request preferences",
15"verify _files": {"file1": "files/notes.txt",
16"file2": "files/problem _specification.txt",
17"file3": "files/request.txt" } },
18"m-understand-flights-tool": {
19"name": "understand flights tool",
20"effect": "notes contains details about flights tool methods inputs and outputs",
21"effect _files": {"file1": "files/notes.txt",
22"file2": "files/tools _specification.txt" } } }
Figure 1: Top: An in-progress HTN decomposition tree for the Travel Planner problem of §1. White boxes
indicate abstract tasks, round ovals indicate methods that decompose tasks, and gray boxes indicate
primitive tasks for the LLM to execute. The dashed box for κ1 indicates it has passed verify. Bottom:
Notional methods for the same problem.
5
