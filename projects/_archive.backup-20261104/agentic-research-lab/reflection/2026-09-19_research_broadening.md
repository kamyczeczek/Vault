---
type: Concept
title: 2026-09-19_research_broadening
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# Session Reflection — Deep Research & Broadening Synthesis

**Date:** 2026-09-19
**Sources:** 9 newly ingested documents + live web research
**Corpus state:** 585 chunks, 107 raw files, graph rebuilt

---

## 1. What Was Researched

Ingested and analyzed:

| Document | Chunks | Core Topic |
|---|---|---|
| `Why Performance Engineering Breaks AI Coding Agents.md` | 6 | Performance engineering failure modes |
| `Theo's AGENTS.md & SKILLS.md Breakdown.md` | 10 | Agent configuration interfaces |
| `You're Using AI Agents Wrong.md` | 4 | Common agent misuse patterns |
| `Building a Practical AI Assembly Line.md` | 5 | Multi-agent orchestration |
| `SkillOpt.md` | 6 | Skill optimization |
| `Can an AI Out-Plan a Senior Engineer.md` | 5 | AI planning capability |
| `Save 20-50% on Agent Tool Call Cost and Latency.md` | 2 | Tool call efficiency |
| `Why New AI Models Rarely Change Everything.md` | 4 | Model capability plateaus |
| `Slop Code Bench.md` | 5 | Code quality degradation benchmark |

---

## 2. Core Findings

### 2.1 Performance Engineering Is the Hardest Agentic Task

**The problem:** General-purpose coding agents fail on performance optimization in three characteristic ways, confirmed by both the ingested corpus and the PerfAgent paper (arXiv 2607.19653):

1. **Missing real bottlenecks** — agents use `cProfile`, which sees only Python-layer frames and misses hotspots inside native extensions (`PyArray_Scalar`, C/Cython/Rust kernels). They stop at the first Python-level fast path they find.
2. **Premature termination** — once a patch passes tests and shows speedup, the agent stops, even when substantial headroom remains.
3. **Insufficient testing** — complex optimizations are tested narrowly, silently breaking edge cases.

**The fix:** PerfAgent demonstrates that a profiler-guided, verifier-in-the-loop workflow more than doubles expert-matching patches (19.6% → 39.2% on GSO; 26% → 74% on SWE-fficiency-Lite) while costing 2–3× less than oracle best-of-5 baselines. The gains come from better feedback, not more compute.

**Key insight:** Performance engineering imposes a stricter requirement than correctness: a patch must preserve behavior AND improve performance, judged against human expert speedups. Current benchmarks hide this because SWE-Bench only tests correctness.

### 2.2 Code Degrades Under Iterative Agent Work

**SlopCodeBench** (arXiv 2603.24755) provides the first measurement of code degradation under iterative extension:

- **No agent fully solved any problem** end-to-end across 36 problems and 196 checkpoints
- Best agent passed only **14.8%** of checkpoints
- **77%** of trajectories showed structural erosion (concentrated complexity)
- **75.5%** showed verbosity growth
- Agent code is **2.3× more verbose** and **2.0× more eroded** than 473 human repositories
- **Explicit quality guidance** reduces initial verbosity/erosion by up to **one third** without affecting degradation rates

**Implication:** Iterative agent workflows need active quality guards—not just correctness checks. Context engineering must include anti-slop mechanisms.

### 2.3 AI Can Out-Plan Senior Engineers, But Not Replace Their Judgment

From `Can an AI Out-Plan a Senior Engineer.md`:

- AI excels at **breadth-first exploration** and **assumption-challenging** via design docs
- It catches inconsistencies humans miss (e.g., missing DTO properties, removed pages)
- It produces **more alternatives** faster than a single human can
- **But:** implementation quality, architectural coherence, and tradeoff evaluation still require senior oversight
- The sweet spot is **AI-assisted planning with human decision-making**

### 2.4 The Refine-Plan-Act Pattern Prevents Context Rot

The RPA pattern (Borzì, 2026) addresses a fundamental agent failure mode: context window pollution from trial-and-error implementation.

**Three independent phases, each in a fresh session:**

1. **Refine:** Transform `TICKET.md` → `REQUIREMENTS.md` by validating against the codebase
2. **Plan:** Transform `REQUIREMENTS.md` → `PLAN.md` with deliberate technical decisions
3. **Act:** Execute `PLAN.md` in a new session; if it fails, discard changes and tweak the plan

**Benefits:**
- Bad output is cheap when thinking is saved separately from code
- Complexity degrades less when each phase has a clear, unambiguous target
- `REQUIREMENTS.md` and `PLAN.md` become reusable artifacts (PR descriptions, docs)
- Cheaper models can execute solid plans, saving tokens

### 2.5 New Models Rarely Change Everything — Workflow Does

From `Why New AI Models Rarely Change Everything.md`:

- Capability improvements are incremental, not discontinuous
- **Workflow/infrastructure changes** produce larger gains than model swaps
- Organizations that invest in agent infrastructure, evaluation, and routing get compounding returns
- Model updates are necessary but insufficient without operational maturity

### 2.6 Tool Call Cost Optimization Is Achievable

`Save 20-50% on Agent Tool Call Cost and Latency.md` documents concrete reductions through:

- Tool call batching
- Result caching
- Selective tool invocation based on confidence thresholds
- Model routing (cheaper models for simpler tasks)

### 2.7 AGENTS.md & SKILLS.md Are Configuration Interfaces

Theo's breakdown reveals that `AGENTS.md` and `SKILLS.md` are not just documentation—they are **agent configuration contracts** that:

- Define model selection per task
- Set cost/capability dials (`maxTurns`, temperature)
- Route tasks to specialized agent configurations
- Provide the "operating system" layer for agent swarms

### 2.8 Agent Design Patterns Are Converging

Web research confirms the corpus findings:

- **Two-dimensional framework:** Cognitive function × execution topology (arXiv 2605.13850)
- **Azure Durable Agents:** Prompt chaining vs. routing vs. agent loops
- **Chief-of-staff routing:** Topic-based agent frontmatter with model/turn controls
- **Execution hooks:** Deterministic loop interception with guardrails

---

## 3. Cross-Cutting Synthesis

### 3.1 The Performance-Planning Gap

Performance engineering and planning are the two areas where agents most need **human-in-the-loop structure**:

- **Performance:** Agents miss cross-abstraction bottlenecks; need profiler-guided iteration
- **Planning:** Agents over-generate but under-evaluate tradeoffs; need human gatekeeping

Both require **artifact preservation** (plans, profiles) separate from execution.

### 3.2 The Slop Problem Compounds

Code degradation isn't a one-shot issue—it accumulates across iterations. This means:

- Single-pass benchmarks underestimate real-world degradation
- Multi-turn agent systems need **quality regression detection**
- Explicit quality constraints in prompts help but don't solve the problem
- The field needs benchmarks like SlopCodeBench that measure erosion, not just pass rates

### 3.3 Workflow > Model

The recurring theme: swapping frontier models yields marginal gains; improving agent workflows yields order-of-magnitude gains:

- PerfAgent: 2× improvement via feedback loops, not model changes
- RPA: quality improvement via phase separation, not prompt tuning
- Tool optimization: 20-50% savings via routing, not model upgrades
- Skill-based routing: better outcomes via specialization, not larger context

---

## 4. Implications for This Workspace

### 4.1 Immediate Research Priorities

1. **Performance engineering agent design** — build profiler-guided loops into coding agents
2. **Anti-slop mechanisms** — develop quality erosion detection for iterative tasks
3. **RPA implementation** — formalize Refine-Plan-Act as a standard agent workflow
4. **Tool call economics** — implement the 20-50% cost optimization patterns

### 4.2 Knowledge Graph Enrichment

New heuristics to promote from this session:

- `profiler-guided-optimization` — performance engineering requires profiler feedback loops
- `anti-slop` — iterative agents need active quality guards
- `artifact-preservation` — separate thinking from execution for recoverability
- `workflow-over-model` — infrastructure changes beat model swaps
- `rpa-pattern` — Refine-Plan-Act for complex agentic coding

### 4.3 Open Questions

- Can SlopCodeBench's erosion detection be integrated into real-time agent monitoring?
- How do we measure "plan quality" independently of implementation correctness?
- What's the optimal balance between fresh-context phases and context continuity?
- Can chief-of-staff routing be automated, or does it require human oversight?

---

## 5. Sources

### Internal Corpus
- 9 newly ingested documents, 47 chunks, now in `knowledge/corpus/`
- Graph rebuilt at fingerprint `eed0c4299be5`

### Web Research
- SlopCodeBench: https://arxiv.org/abs/2603.24755
- PerfAgent: https://arxiv.org/pdf/2607.19653v1
- RPA Pattern: https://medium.com/engineering-in-the-age-of-ai/the-refine-plan-act-pattern-for-agentic-ai-coding-59ee013e4427
- Agent Design Patterns Framework: https://arxiv.org/html/2605.13850v2
- Azure Durable Agents: https://learn.microsoft.com/en-us/azure/durable-task/sdks/durable-agents-patterns

---

*Reflection generated 2026-09-19. Ready for meta-learning integration.*
