---
type: Concept
title: workspace-remodeling-guide
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

The research suggests a useful upgrade to the previous approach: the agent should not begin by proposing files or rewriting `AGENTS.md`. It should first **map the existing workspace, identify friction and architectural weaknesses, research relevant patterns, and produce a bounded remodeling plan**.

The strongest current evidence points toward treating the workspace as a **harness** with explicit components, observability, verification, permissions, failure attribution, and reversible evolution—not merely as a collection of prompts and skills. ([arXiv](https://arxiv.org/abs/2605.13357?utm_source=chatgpt.com)) SkillOpt further supports treating skills/workspace changes as bounded optimization experiments with validation and rejected-change memory. ([Microsoft](https://www.microsoft.com/en-us/research/blog/skillopt-agent-skills-as-trainable-parameters/?utm_source=chatgpt.com))

Here is the guide I would give your AI agent.

# Workspace Remodeling & Self-Improvement Research Guide

## Mission

Your job is **not** to immediately modify this workspace.

Your first job is to understand it, research how similar agent workspaces are engineered, identify where the current workspace creates unnecessary friction, and produce a practical remodeling plan.

The long-term objective is:

> Make the workspace progressively easier, safer, more predictable, and less dependent on human correction.

Do not optimize for "more instructions", "more memory", or "more automation" by default.

Optimize for:

- fewer repeated mistakes
- fewer human corrections
- fewer unnecessary decisions
- easier discovery of the correct action
- stronger automatic verification
- lower context burden
- lower regression risk
- easier recovery
- better generalization to unfamiliar tasks

------

# 1. First principle

Treat the workspace as an **environment/harness around the agent**.

The agent itself is only one component.

Investigate:

```text
                    WORKSPACE / HARNESS

        ┌──────────────┬───────────────┬──────────────┐
        │              │               │              │
     context         tools          structure      skills
        │              │               │              │
        ├──────────────┼───────────────┼──────────────┤
        │              │               │              │
    retrieval       execution       constraints    procedures
        │              │               │              │
        └──────────────┼───────────────┼──────────────┘
                       │
                    AGENT
                       │
                    TASKS
                       │
                  OBSERVATIONS
                       │
                  VERIFICATION
                       │
                    FEEDBACK
```

Recent harness-engineering research explicitly treats task specification, context selection, tools, project memory, state, observability, failure attribution, verification, permissions, and intervention recording as distinct responsibilities of the agent runtime. ([arXiv](https://arxiv.org/abs/2605.13357?utm_source=chatgpt.com))

Therefore, when you find a recurring problem, do not automatically classify it as a "knowledge problem".

It may be:

- a tool problem
- a workflow problem
- a retrieval problem
- a structural problem
- a verification problem
- a permission problem
- an observability problem
- a skill problem
- an instruction problem
- or simply an unavoidable human judgment

------

# 2. Phase 0 — Establish the remodeling boundary

Before changing anything, determine:

1. What directory is the workspace?
2. Which files are authoritative?
3. Which files are generated?
4. Which files are disposable?
5. Which tools can modify the workspace?
6. Which files should the agent never modify automatically?
7. How are tasks currently represented?
8. How are tests/checks currently represented?
9. How is previous experience stored?
10. Where can an experimental change be isolated and reverted?

Do not assume that the workspace follows the proposed:

```text
workspace/
tasks/
tools/
checks/
skills/
lessons/
.workspace/
```

structure.

That structure is a hypothesis, not a requirement.

------

# 3. Phase 1 — Inventory the existing workspace

Create an inventory before proposing improvements.

Inspect:

```text
directories
important files
configuration
instructions
scripts
tests
tool definitions
skills
memory
logs
state
generated artifacts
documentation
CI/checks
permissions
entry points
```

For each important component, determine:

```yaml
component:
purpose:
inputs:
outputs:
who_modifies_it:
who_consumes_it:
failure_modes:
verification:
reversible:
importance:
```

Do not rewrite anything yet.

Produce a short architecture map.

Example:

```text
AGENTS.md
    ↓
agent instructions

tools/
    ↓
manual capabilities

checks/
    ↓
verification

skills/
    ↓
procedural knowledge

tasks/
    ↓
real work

logs/
    ↓
experience
```

Then compare that map with the actual workspace.

------

# 4. Phase 2 — Identify friction

Search the workspace for evidence of friction.

Look for:

- repeated TODOs
- repeated warnings
- comments saying "remember"
- duplicated instructions
- manual recovery procedures
- scripts that users repeatedly invoke manually
- failed tests
- workaround scripts
- stale documentation
- repeated exception handling
- contradictory instructions
- duplicated skills
- oversized instruction files
- unused tools
- abandoned experiments
- repeated human intervention
- places where the agent must guess

Also inspect recent task history if available.

Classify each friction item:

```text
knowledge
retrieval
tool
workflow
structure
verification
observability
permission
state/memory
human judgment
unknown
```

Do not propose solutions yet.

------

# 5. Phase 3 — Measure before remodeling

Construct a baseline.

At minimum estimate:

```text
task success
human interventions
human corrections
agent retries
failed checks
repeated failures
time to completion
context/token burden
tool failures
regressions
```

If historical data does not exist, explicitly mark the baseline as:

```text
UNKNOWN
```

Do not invent measurements.

The first remodeling plan should include a way to start collecting the missing measurements.

------

# 6. Phase 4 — Research before recommending

Perform targeted web research.

Do not search for generic "best AI agent workspace" advice.

Research concrete mechanisms and experiments.

Prioritize:

### A. Harness engineering

Research:

- agent harness architecture
- tool design
- workflow automation
- context engineering
- verification
- observability
- failure attribution
- intervention recording
- self-improving harnesses

Agentic Harness Engineering is particularly relevant because it treats every editable harness component as explicit and reversible, distills trajectory evidence, and associates changes with falsifiable predictions. ([arXiv](https://arxiv.org/abs/2604.25850?utm_source=chatgpt.com))

### B. Skill optimization

Research:

- SkillOpt
- bounded skill edits
- held-out validation
- rejected-edit memory
- add/delete/replace
- best-known artifact
- transfer across models/harnesses

SkillOpt treats an external skill artifact as trainable state and reports validation-gated improvement across multiple models, benchmarks, and execution harnesses. ([Microsoft](https://www.microsoft.com/en-us/research/blog/skillopt-agent-skills-as-trainable-parameters/?utm_source=chatgpt.com))

### C. Online harness evolution

Research:

- Evo-Harness
- HarnessEvolve
- continual workspace evolution
- context-to-skill compilation
- reference trajectories
- credit assignment
- catastrophic forgetting
- shortcut learning

Recent work on HarnessEvolve specifically identifies credit assignment, task-specific shortcut learning, and catastrophic forgetting as problems for self-evolving harnesses and uses separate execution, evaluation, optimization, and gating roles. ([arXiv](https://arxiv.org/abs/2609.00829?utm_source=chatgpt.com))

Evo-Harness explores converting noisy one-shot executions into reusable skill/harness adaptations across realistic tasks. ([arXiv](https://arxiv.org/abs/2608.15071?utm_source=chatgpt.com))

### D. Context-file effectiveness

Research whether adding instructions actually improves results.

Do not assume:

```text
more context = better agent
```

The available evidence gives reason to be skeptical: evaluations of persistent repository context have found cases where it increased cost without improving correctness. ([Microsoft](https://www.microsoft.com/en-us/research/blog/skillopt-agent-skills-as-trainable-parameters/?utm_source=chatgpt.com))

Therefore investigate:

- context selection
- retrieval
- instruction bloat
- skill routing
- context compression
- stale instructions
- contradictory instructions

### E. Reliability engineering

Research:

- regression prevention
- independent evaluation
- rollback
- permission boundaries
- reproducibility
- deterministic checks
- safe experimentation
- auditability

A recent systematic review of coding-agent reliability argues that many apparent "model failures" originate elsewhere in the system—retrieval, execution state, verification, permissions, memory, or observability. ([arXiv](https://arxiv.org/abs/2608.13867?utm_source=chatgpt.com))

------

# 7. Separate evidence from inspiration

For every researched mechanism, record:

```yaml
idea:
source:
evidence_type:
experiment:
reported_result:
limitations:
relevance_to_this_workspace:
confidence:
```

Use these evidence categories:

```text
A = replicated / strong evidence
B = credible experimental evidence
C = promising but limited
D = conceptual idea
```

Do not present a D-level idea as established fact.

Especially distinguish:

```text
"researchers reported this worked"
```

from:

```text
"this should work here"
```

The second is a hypothesis.

------

# 8. Diagnose the workspace before choosing an architecture

For every major problem, ask:

## Question 1

Can the workspace structure make the mistake impossible?

If yes:

```text
STRUCTURAL CHANGE
```

Prefer this.

## Question 2

If not, can an automated check detect it?

```text
CHECK
```

## Question 3

If not, can a tool make the correct behavior easy?

```text
TOOL
```

## Question 4

If the behavior requires judgment or repeated procedure, can it become a reusable skill?

```text
SKILL
```

## Question 5

Can retrieval be improved instead of adding another skill?

```text
RETRIEVAL
```

## Question 6

Can the workflow automate the decision?

```text
WORKFLOW
```

## Question 7

Only if none of the above works:

```text
INSTRUCTION
```

## Question 8

If the decision genuinely requires human judgment:

```text
HUMAN CHECKPOINT
```

Use this preference:

```text
structure
    >
check
    >
tool
    >
workflow
    >
retrieval
    >
skill
    >
instruction
    >
human correction
```

This is a preference, not an absolute law.

Risk, flexibility, implementation cost, and false-positive rate may justify choosing a lower level.

------

# 9. Look for "knowledge that should become infrastructure"

This is one of the highest-priority analyses.

For every recurring instruction, ask:

> Does this really need to remain knowledge?

Example:

```text
"Always run the API tests."
```

Possible better forms:

```text
tool:
    tools/test-api.sh

check:
    checks/api-validation.sh

workflow:
    completion automatically invokes validation
```

The remodeling objective is to move recurring knowledge toward infrastructure when doing so reduces cognitive load without excessive rigidity.

The desired transformation is:

```text
human remembers
      ↓
agent remembers
      ↓
skill
      ↓
tool
      ↓
check
      ↓
structure / automation
```

------

# 10. Search for unnecessary decision points

Identify decisions the agent repeatedly has to make.

Examples:

```text
Which command?
Which directory?
Which test?
Which configuration?
Which tool?
Which format?
Which file?
Which workflow?
```

For each, ask:

> Is this a real judgment or unnecessary workspace ambiguity?

If unnecessary, remove the decision.

The target is not maximum autonomy.

The target is:

> **minimum unnecessary decision-making.**

------

# 11. Search for missing affordances

Ask:

> What should be obvious from the workspace but currently isn't?

Examples:

```text
No obvious way to run tests
No obvious task template
No standard entry point
No obvious validation command
No obvious failure report
No obvious place for generated output
No obvious recovery mechanism
No obvious way to inspect task state
```

Prefer creating affordances over adding explanations.

------

# 12. Analyze the existing instructions

For every instruction file:

Measure approximately:

```text
length
number of rules
number of exceptions
duplicated concepts
stale rules
contradictions
rules that could be automated
rules that could become checks
rules that could become tools
rules that are actually unnecessary
```

Do not expand instructions simply because something went wrong.

A failed task is evidence that something in the system may need improvement.

It is not automatically evidence that another sentence is needed.

------

# 13. Analyze skills

For every skill:

```yaml
skill:
trigger:
purpose:
inputs:
procedure:
verification:
usage_frequency:
success_evidence:
failure_evidence:
context_cost:
overlap:
last_validated:
status:
```

Classify skills:

```text
active
candidate
obsolete
duplicated
too broad
too narrow
poorly retrieved
not validated
```

Look specifically for:

### Skill exists but isn't retrieved

This is a retrieval problem.

Do not create another skill.

### Skill is retrieved but ignored

Investigate usability, relevance, or conflicting instructions.

### Skill is repeatedly useful

Consider promotion into a more stable mechanism.

### Skill is encoded elsewhere

Merge or delete it.

------

# 14. Analyze tools

For each tool ask:

```text
Is it discoverable?
Is it easy to invoke?
Does it have predictable inputs/outputs?
Does it fail clearly?
Does it validate its own result?
Is it redundant?
Could it replace repeated instructions?
Could it safely be made the default?
```

Look for "wrapper opportunities".

For example:

```text
10 agents repeatedly execute:

python -m pytest tests/api --config x --foo y
```

Consider:

```text
tools/test-api
```

The tool becomes the stable interface.

------

# 15. Analyze checks

Checks should not merely exist.

Ask:

```text
What failure does each check catch?
How often does it catch something useful?
How many false positives?
How expensive is it?
Can it run automatically?
Does the agent understand the failure?
```

A bad check creates friction.

A good check converts invisible failure into actionable feedback.

------

# 16. Design an evaluation boundary

Never allow the remodeling process to decide that a change is good solely because the agent says it is good.

For every candidate workspace change define:

```text
baseline
candidate
test tasks
success metric
regression metric
cost metric
acceptance rule
rollback rule
```

Prefer:

```text
development/evolution tasks
        ≠
validation tasks
```

Keep some tasks hidden from the optimizer.

SkillOpt's validation-gated approach is a useful model here, as is HarnessEvolve's use of recent-batch protection plus held-out validation. ([Microsoft](https://www.microsoft.com/en-us/research/publication/skillopt-executive-strategy-for-self-evolving-agent-skills/?utm_source=chatgpt.com))

------

# 17. Protect against workspace bloat

Every proposed addition must answer:

```text
What does this replace?
What problem does it solve?
What evidence supports it?
What does it cost?
When should it be removed?
```

Avoid:

```text
more files
more skills
more instructions
more memory
more checks
```

as goals in themselves.

Measure:

```text
workspace complexity
context cost
active skill count
instruction size
tool count
check count
retrieval burden
```

The workspace should be able to become **smaller while becoming better**.

------

# 18. Design for deletion

Every remodeling proposal must include a cleanup strategy.

For every component:

```yaml
removal_condition:
revalidation_period:
replacement:
dependencies:
```

Candidate states:

```text
proposed
experimental
accepted
deprecated
rejected
removed
```

Never treat "existing" as equivalent to "useful".

------

# 19. Design negative knowledge

Maintain:

```text
.workspace/rejected/
```

Record:

```yaml
candidate:
problem:
attempted_change:
result:
why_rejected:
evidence:
do_not_repeat_when:
```

Negative results are part of the workspace's experimental history.

But do not turn rejected experiments into permanent instructions.

------

# 20. Separate the roles

Do not let one unconstrained agent:

```text
execute task
judge itself
modify workspace
declare improvement
```

Prefer conceptual separation:

```text
EXECUTOR
    ↓
produces task result

OBSERVER
    ↓
extracts evidence

DIAGNOSTICIAN
    ↓
proposes root cause

OPTIMIZER
    ↓
proposes workspace change

EVALUATOR
    ↓
tests candidate

GATE
    ↓
accept / reject

HISTORY
    ↓
records outcome
```

The same model may perform multiple roles initially, but keep the roles conceptually separate.

This makes later automation and auditing much easier.

------

# 21. Look for transfer

A remodeling change is more interesting if it helps:

```text
task A
task B
task C
```

rather than only:

```text
the exact task that produced the lesson
```

For every proposed improvement ask:

> What other task family should this help?

Then create a small transfer test.

This guards against memorizing individual tasks rather than improving the workspace.

Recent self-evolving harness research specifically studies whether evolved changes transfer across languages, models, and task families rather than merely fitting the workload that produced them. ([arXiv](https://arxiv.org/abs/2608.10178?utm_source=chatgpt.com))

------

# 22. Produce a remodeling map

After research and inspection, create a table:

| Current problem        | Root cause         | Proposed mechanism | Evidence | Risk   | Cost   | Validation     |
| ---------------------- | ------------------ | ------------------ | -------- | ------ | ------ | -------------- |
| repeated wrong command | discoverability    | tool               | B        | low    | low    | 5 tasks        |
| forgotten validation   | workflow           | automatic check    | B        | low    | low    | 5 tasks        |
| huge instructions      | context bloat      | remove/restructure | A/B      | low    | low    | benchmark      |
| duplicated skills      | poor consolidation | merge              | C        | low    | low    | transfer tasks |
| unclear failures       | observability      | structured report  | B        | medium | medium | failure replay |

Do not implement the entire table.

Rank it.

------

# 23. Prioritize by expected value

Use a simple score:

```text
Priority =
    frequency
  × human_cost
  × recurrence
  × confidence
  × expected_generalization
  /
    implementation_cost
```

Then separately account for risk.

A dangerous high-impact change should not automatically win just because it has a high score.

------

# 24. Produce three remodeling horizons

## Horizon 1 — Immediate

Changes that are:

- low risk
- reversible
- cheap
- directly supported by evidence

Usually:

```text
better check
better tool
cleanup
clearer structure
better logging
```

## Horizon 2 — Experimental

Changes requiring validation:

```text
skill routing
automatic candidate generation
new workflow
automatic task validation
experience consolidation
```

## Horizon 3 — Research

Do not implement yet.

Examples:

```text
autonomous workspace optimizer
sleep-cycle consolidation
automatic structural evolution
cross-project skill transfer
risk-adaptive promotion
causal failure attribution
```

------

# 25. Research deeper when you encounter these questions

Maintain a research backlog.

Prioritize:

### R1 — What should be learned?

Compare:

```text
instructions
skills
tools
checks
workflow
structure
```

### R2 — What should trigger learning?

Compare:

```text
failure
human correction
success
near miss
efficiency gain
repeated pattern
```

### R3 — How much evidence is enough?

Test:

```text
1 occurrence
2
3
5
10
```

Do not assume a universal threshold.

### R4 — How do we detect causality?

A change may coincide with improvement without causing it.

### R5 — How do we prevent regressions?

Study:

```text
held-out validation
recent-task protection
best-known snapshots
rollback
```

### R6 — How should skills be organized?

Compare:

```text
global skill
per-task skill
procedural families
retrieval-based library
```

### R7 — How should obsolete knowledge disappear?

Study:

```text
decay
revalidation
usage-based deletion
merge
replacement
```

### R8 — How do we detect retrieval failure?

If a useful skill exists but wasn't retrieved, adding another skill is the wrong intervention.

### R9 — How do we learn from success?

Identify what made successful tasks easy.

### R10 — How do we optimize human effort?

Treat human corrections and intervention time as first-class outcomes.

### R11 — How do we prevent context bloat?

Measure quality against context cost.

### R12 — How do we transfer improvements?

Test across unseen tasks and task families.

### R13 — How do we attribute failure?

Use structured trajectories rather than only final success/failure.

### R14 — How do we safely automate remodeling?

Separate proposal, evaluation, and promotion.

------

# 26. Do not prematurely build a "self-improving AI"

The first target is much smaller:

```text
workspace remodeling assistant
```

Its job is:

```text
inspect
  ↓
research
  ↓
diagnose
  ↓
propose
  ↓
prioritize
  ↓
experiment
  ↓
evaluate
```

Not:

```text
autonomously rewrite everything
```

The distinction is important.

------

# 27. The desired evolution

The remodeling process should gradually move through:

```text
LEVEL 0
Human notices everything

        ↓

LEVEL 1
Workspace records friction

        ↓

LEVEL 2
Agent analyzes friction

        ↓

LEVEL 3
Agent proposes guardrails

        ↓

LEVEL 4
Agent evaluates candidate guardrails

        ↓

LEVEL 5
Human approves validated changes

        ↓

LEVEL 6
Low-risk changes can be automatically promoted

        ↓

LEVEL 7
Human handles only ambiguous/high-risk changes
```

Do not skip directly to Level 7.

------

# 28. Final deliverable

After inspecting and researching the workspace, produce:

## A. Workspace map

What exists and what each component does.

## B. Friction map

Top recurring sources of difficulty.

## C. Research findings

Only evidence relevant to this workspace.

## D. Contradictions

Where current assumptions appear wrong.

## E. Remodeling hypotheses

Each expressed as:

```yaml
problem:
hypothesis:
proposed_change:
expected_effect:
risk:
evidence:
validation:
rollback:
```

## F. Prioritized roadmap

```text
P0 — do now
P1 — test next
P2 — research
```

## G. Explicit non-changes

List things you recommend **not** changing.

This is important.

A good remodeling plan should explain why some parts of the workspace should remain untouched.

------

# 29. Most important constraint

Do not remodel for elegance.

Remodel because evidence suggests:

```text
current behavior
        ↓
repeated friction
        ↓
root cause
        ↓
specific intervention
        ↓
measurable improvement
```

If you cannot connect those five steps, label the idea:

```text
SPECULATIVE
```

and don't implement it yet.

------

# 30. North-star objective

The workspace should gradually approach this state:

```text
                    HUMAN
                      │
                 gives intent
                      │
                      ▼
                    AGENT
                      │
          workspace handles routine
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
      tools         checks        skills
        │             │             │
        └─────────────┼─────────────┘
                      ▼
                  good result
                      │
                      ▼
                   evidence
                      │
                      ▼
              workspace improves
```

The ultimate measure is not:

> "How much knowledge has the workspace accumulated?"

It is:

> **"How little expertise, remembering, correcting, and babysitting does the human need to provide for the workspace to reliably produce good results?"**

When remodeling the workspace, optimize toward that outcome.

### One additional instruction I would give the agent

Ask it to produce **a plan before touching anything**.

That gives you a useful safety boundary:

```text
inspect → research → plan → human review → implement → validate
```

rather than:

```text
inspect → immediately rewrite workspace
```

That separation is particularly well supported by the recent harness-evolution literature: execution, evaluation, optimization, and gating are increasingly treated as separable responsibilities, precisely because otherwise self-modification can turn into uncontrolled drift. ([arXiv](https://arxiv.org/abs/2609.00829?utm_source=chatgpt.com))

And I would explicitly tell the agent that **"make it simpler" is a valid successful remodeling outcome**. A workspace with fewer instructions, fewer skills, fewer tools, and fewer human interventions is potentially better than a more sophisticated workspace. Recent work on evolved harnesses also suggests that gains often come from correcting concrete execution defects rather than adding generalized prose. ([arXiv](https://arxiv.org/abs/2608.10178?utm_source=chatgpt.com))