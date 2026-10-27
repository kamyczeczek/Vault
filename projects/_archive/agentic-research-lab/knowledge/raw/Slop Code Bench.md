---
type: Concept
title: Slop Code Bench
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# A Structured Guide to the "Slop Code Bench" AI Coding Agent Benchmark

## Based on the "AI That Works" Podcast Discussion

---

## Executive Summary

**Slop Code Bench** is a new benchmark for evaluating AI coding agents, designed to test whether models can build **maintainable software** over time—not just solve isolated coding problems. The benchmark reveals that even the best frontier models achieve only ~33% strict pass rates, exposing a critical gap between "does the code work now?" and "will it be easy to extend and maintain?"

**Key Insight:** Current models are decent at solving the problem directly in front of them, but they accumulate defects and complexity ("slop") as they iterate—mirroring real-world software development challenges.

---

## 1. What Is Slop Code Bench?

### 1.1 The Problem It Solves

Traditional coding benchmarks (like SWE-bench) have limitations:
- They give you the **whole problem upfront**
- They test **can you solve it?** not **will it remain maintainable?**
- They're often **saturated** (models score too high to differentiate)

### 1.2 The Slop Code Bench Approach

| Feature                    | Description                                                  |
| -------------------------- | ------------------------------------------------------------ |
| **Sequential Checkpoints** | Models receive an initial spec, then incrementally harder requirements |
| **Code Inheritance**       | Each new challenge builds on the existing codebase (no fresh start) |
| **Unsaturated**            | Top models score only ~33% strict pass rate                  |
| **Blackbox Testing**       | Tests are language-agnostic (CLI or HTTP interfaces)         |
| **Slop Detection**         | 200+ metrics measuring code quality degradation              |

### 1.3 Creator & Origin

- **Creator:** Gabe Oransky (University of Wisconsin–Madison)
- **Published:** March 2024 (initial paper); results updated regularly
- **Website:** slopcodebench.com

---

## 2. How the Benchmark Works

### 2.1 The Challenge Structure

```
Checkpoint 1 → Write initial code
     ↓
Checkpoint 2 → Add feature A (inherits codebase)
     ↓
Checkpoint 3 → Add feature B (inherits codebase)
     ↓
...up to 8+ checkpoints per challenge
```

**Example: XJQ Challenge**
1. Build `jq` for XML (parse XML from stdin, select elements)
2. Add CSS selector support
3. Add JSON object/array support
4. Read from files instead of stdin (UTF-8 support)
5. Add JSON export functionality
6. ...progressively evolve into a generic serializer/deserializer

### 2.2 Key Metrics

| Metric                 | Definition                                                   |
| ---------------------- | ------------------------------------------------------------ |
| **Strict Pass Rate**   | Model passes ALL tests across ALL checkpoints (no regressions) |
| **Isolated Pass Rate** | Model passes tests for current checkpoint (regardless of past failures) |
| **Defect Count**       | Number of failing blackbox tests accumulated over time       |
| **Cost**               | Total inference cost per challenge                           |

### 2.3 Why Strict Pass Rate Matters

- **Isolated Pass:** "Did you solve the new thing?"
- **Strict Pass:** "Did you solve the new thing AND not break anything?"

> *"It's kind of like when coding agents work—it's like, what am I really solving for? Have I solved the current problem in front of me and have I accidentally broken anything in the past?"*

---

## 3. Key Findings

### 3.1 Model Performance (Strict Pass Rates)

| Model        | Strict Pass Rate | Notes                                 |
| ------------ | ---------------- | ------------------------------------- |
| **Fable 5**  | ~33%             | Tied for best                         |
| **Soul**     | ~33%             | Tied for best; best on Circuit Eval   |
| **Kimi K2**  | ~30-33%          | Varies by provider (Modal vs. Base10) |
| **GPT-5.5**  | ~14.8%           | Lower performance                     |
| **Opus 5**   | ~23-25%          | From earlier runs                     |
| **Opus 4.8** | ~6%              | Older generation                      |

### 3.2 Defect Accumulation

- **All models accumulate defects** as checkpoints progress
- **Soul** performed worst on defect accumulation in some challenges
- **No model** maintained perfect code quality across all checkpoints

### 3.3 Cost vs. Quality

```
Higher Cost → Generally Better Results
     ↓
But diminishing returns
     ↓
Fable: 2% better than Soul at 5x the cost
```

**Key insight:** For most use cases, paying 5x more for marginal improvement is a bad spend—but for critical applications, it may be worth it.

### 3.4 Code Quality Metrics

| Metric                            | Finding                                                      |
| --------------------------------- | ------------------------------------------------------------ |
| **Cyclomatic Complexity**         | Kimi K3 showed 5x increase across checkpoints                |
| **Code Duplication**              | Models roughly equivalent                                    |
| **Function Count vs. Complexity** | Inverse relationship (more functions = simpler functions)    |
| **Slop Detection**                | 95% of Soul's code triggered at least one slop rule (but rules are aggressive) |

---

## 4. Surprising Insights

### 4.1 Planning Mode Doesn't Help (Much)

> *"They asked all models to write a plan and then solve it, and they asked them all to just solve it—and it doesn't matter."*

**Why planning used to matter:**
- It was a **checkpointing system** to make models work longer
- It increased the scope of unattended work

**Why it doesn't matter now:**
- Models are RL-trained to work longer
- The benefit of planning is gone

**What works instead:**
- **Design concept:** Shared understanding in the context window (not written to file)
- **Surface area definition:** Agree on interfaces, not full execution plans
- **Ralph Wiggum style:** Launch sub-agents per phase, check between phases

### 4.2 Models Don't Refactor Mid-Stream

> *"Could you imagine if it decided to just refactor your whole system and say, 'No, this is just wrong'? I rarely see it do that."*

- Models follow patterns established by earlier checkpoints
- If checkpoint 1 uses scripts for testing, checkpoint 8 will too
- No model has shown the ability to "step back" and make orthogonal architectural decisions

### 4.3 Skills & Context Files (AGENTS.md)

**Recommendation from hosts:**

| Practice            | Advice                                                       |
| ------------------- | ------------------------------------------------------------ |
| **AGENTS.md**       | Delete by default; add only if proven necessary              |
| **Skills**          | Only for things NOT in model weights (e.g., custom type systems) |
| **CLAUDE.md**       | Throw out when new models release                            |
| **Burden of proof** | On the developer to justify keeping skills                   |

> *"Every time there's a new model, you should throw out your AGENTS.md and your CLAUDE.md and all your skills."* — Boris Cherney (cited approvingly)

**When skills ARE valuable:**
- Edge teams (10-20 people) doing same workflow
- Custom type systems not in training data
- Monorepo navigation ("ignore 99% of the repo")
- Standardizing workflows across a team

**What's NOT needed anymore:**
- "Always run tests after changes" (models do this)
- GitHub CLI usage (models know it)
- Agent browser (models know it)

---

## 5. Proposed Improvements to the Benchmark

### 5.1 Give the Whole Spec Upfront

**Hypothesis:** Models would perform significantly better if given all checkpoints at once.

> *"What do the best engineers do? The best engineers provide all the context upfront. If that's true, the takeaway is not that these models are bad at long horizon—it's that humans who are best at using models are the ones who can predict the feature the best."*

### 5.2 Smaller Model Handoff Test ("Super Strict Pass")

**Proposal:** After a frontier model completes checkpoint N, a smaller model (e.g., Sonnet) attempts checkpoint N+1.

- If the smaller model **aces** it → frontier model gets "super strict pass"
- This tests whether the frontier model set up the codebase for **future maintainability**
- Simulates real-world handoff scenarios

### 5.3 Deterministic Linters as Feedback Loop

**Proposal:** Apply linters during the challenge (not just after).

- Cap cyclomatic complexity
- Force clean code patterns
- Simulates real-world "lights off" software factories
- Tests whether cross-model review (Fable reviews Soul, Soul reviews Fable) improves outcomes

---

## 6. Practical Takeaways

### 6.1 For Individual Developers

| Do                                       | Don't                                 |
| ---------------------------------------- | ------------------------------------- |
| Iterate fast, ship small                 | Over-plan upfront                     |
| Use models for compression of time       | Cargo cult skills from model to model |
| Define surface area, not execution plans | Assume planning mode is necessary     |
| Test with blackbox interfaces            | Trust that code is maintainable       |

### 6.2 For Teams

| Do                                           | Don't                                           |
| -------------------------------------------- | ----------------------------------------------- |
| Measure skill effectiveness with evals       | Add skills everywhere by default                |
| Use skills for org-specific workflows        | Assume skills transfer across model generations |
| Build context shards from common corrections | Ignore model weight improvements                |
| Standardize on minimal context               | Fight the model with excessive instructions     |

### 6.3 For Tool Builders

- **MCPs** can help (e.g., efficient code search)
- **Skills** should be purpose-built, not universal
- **Harnesses** should be customizable (add skills, change prompts)
- **Cross-model review** is promising (Fable reviews Soul, etc.)

---

## 7. The Bigger Picture

### 7.1 What "Lights Off" Would Require

> *"What signal would I have to see in the benchmark data to tell me, 'Oh my god, a model wrote four checkpoints of code and then GPT-OSS 12B was able to solve the next checkpoint'? That is a sign."*

**Requirements for fully autonomous coding:**
1. Frontier model sets up codebase that **smaller models can extend**
2. No regressions across checkpoints
3. Code quality remains stable or improves
4. Model demonstrates **unique insight** (not just pattern matching)

### 7.2 The Current State (2026)

> *"Everyone is trying to figure out what code do you still have to read, what code can you not read, how do you maximize confidence, and how do you avoid disaster."*

**Key tension:**
- **Infrastructure/algorithm design:** Predict workload, design architecture upfront
- **Product development:** Ship small, iterate fast, assume customer knows more

**Resolution:** Different domains require different approaches. Benchmarks like Slop Code Bench help us understand **where models excel** and **where humans still add value**.

---

## 8. Resources

| Resource                    | Link/Reference                                 |
| --------------------------- | ---------------------------------------------- |
| **Slop Code Bench Website** | slopcodebench.com                              |
| **Paper**                   | Published March 2024 by Gabe Oransky           |
| **Dexter's Article**        | "Testing Opus 5 on Slop Code Bench"            |
| **Podcast**                 | "AI That Works" (Tuesdays, 10:15am PT)         |
| **Unconference**            | SF-based, attendee-driven, Chattam House rules |

---

## 9. Conclusion

Slop Code Bench fills a critical gap in AI coding benchmarks by testing **maintainability**, not just **solvability**. Key findings:

1. **Best models achieve ~33% strict pass rate** — far from solved
2. **All models accumulate defects** as complexity grows
3. **Planning mode provides little benefit** with modern RL-trained models
4. **Skills and context files should be minimal** — only for things not in weights
5. **Cost correlates with quality** but with diminishing returns

**The future of benchmarking** may include:
- Full-spec upfront comparisons
- Smaller-model handoff tests
- Deterministic linters as feedback loops

**The ultimate question:** What signal would convince you to go "lights off" and let AI agents build software without human review?

---

*Guide compiled from the "AI That Works" podcast episode featuring Vibov and Dexter discussing Slop Code Bench results and implications.*