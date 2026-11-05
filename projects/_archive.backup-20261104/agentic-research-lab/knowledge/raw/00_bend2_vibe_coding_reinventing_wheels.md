---
id: 00_bend2_vibe_coding_reinventing_wheels
 title: "Bend 2, Vibe Coding, and the Case for Deliberate Reinvention"
source: "Liam Powell, Bend 2 and the Vibe-Coding Trap; Bend 2 documentation; comparative coverage of SPARK, Lean, and Dafny"
tags: [agentic-engineering, vibe-coding, formal-verification, proof-systems, software-architecture, research-methodology]
trust_tier: 1
---

# Research question

When an AI-assisted project appears to reinvent an existing technical discipline, when is that a failure of research, and when can reinvention be a legitimate research experiment?

# Evidence gathered

## Bend 2 controversy

Liam Powell's September 2026 critique uses Bend 2 as an example of a vibe-coding failure mode: a developer can produce a substantial language and compiler before discovering that formal verification already provides mature techniques and tools. The critique compares Bend's homepage demonstration with a SPARK recreation and reports that the Bend example uses roughly 58 lines of laws and 442 lines of proof, while SPARK discharges the comparable checks automatically through GNATprove.

The relevant lesson is not simply that shorter code is better. It is that an AI can follow a framing literally and never volunteer the prior-art search that would reveal adjacent disciplines, established toolchains, or better abstractions.

## Counterargument

The Bend author's response, as summarized in the discussion, argues that explicit proofs are intentional and may trade verbosity for proof-checking speed, predictable checking, or a different division of labor between humans and models. Bend's own proof documentation shows that laws and proofs are explicit language constructs. Comparative coverage also emphasizes that Bend's bet differs from SPARK, Dafny, and Lean: it moves more proof construction onto the model while providing less automation and fewer mature libraries.

Therefore, line count alone does not establish inferiority. A valid comparison must include proof effort, checker cost, compiler/runtime targets, automation, library maturity, auditability, model success rates, and total engineering cost.

# Synthesis for agentic-research-lab

Our memory-system work is in the same danger zone, but the conclusion should be more precise than "do not reinvent wheels."

The defensible position is **deliberate, bounded reinvention**:

1. Identify prior art before implementation.
2. State the gap that existing tools do not satisfy.
3. Make the custom component a reversible experiment.
4. Preserve authoritative source-of-truth boundaries.
5. Define an evaluation baseline before expanding the feature.
6. Keep explicit proof artifacts for safety, privacy, integrity, and provenance.

Our separate SQLite/JSONL/Markdown stores and rebuildable projections are defensible hypotheses because they target determinism, inspectability, privacy, deletion boundaries, and local operation together. They are not proof that the architecture is superior to an existing memory framework.

The local context gateway retrieved accepted lessons supporting this synthesis:

- `verified-self-evolution-gates`: generated updates need explicit formal or environment-based verification before state commitment.
- `agent-sandboxing`: exploratory actions need isolated verification environments before canonical state changes.
- `mandatory-deep-technical-analysis`: technical sources should be analyzed beyond superficial summaries.
- `minimalist-script-harness`: transparent scripts can be preferable to opaque frameworks for core verification.

These lessons support using the gateway as a research instrument, but they also impose a discipline on it: every new custom subsystem needs a prior-art record, an evidence-backed hypothesis, an acceptance proof, and a removal plan.

# Claims and limits

- **Supported:** AI-assisted development can produce coherent implementations without adequate prior-art discovery. Powell's Bend critique and the comparative coverage directly support this warning.
- **Supported:** formal-verification ecosystems such as SPARK, Lean, and Dafny provide prior art relevant to AI-generated proof workflows.
- **Not established:** Bend 2 is categorically worse than those systems. The available comparison highlights tradeoffs but does not provide a comprehensive benchmark.
- **Not established:** verbosity reliably improves proof-checking speed. That is a design claim requiring measurements.
- **Not established:** our custom memory architecture improves agent task outcomes. We have foundation proofs, not a representative retrieval benchmark.

# Follow-up experiments

1. Build a prior-art matrix for workspace memory: direct SQLite/FTS, vector retrieval, graph databases, hosted agent memory, event sourcing, and workflow state stores.
2. Compare the unified gateway against direct source-specific retrieval on representative continuation tasks.
3. Measure retrieval precision, supported-answer rate, latency, estimated context cost, and workspace-leakage failures.
4. For each custom component, record whether the result is a deliberate reinvention, exploratory prototype, or accidental duplication.
5. Add an explicit "stop or adopt" gate so the project does not grow indefinitely through locally plausible patches.

# Sources

- Liam Powell, "Bend 2 and the Vibe-Coding Trap," https://blog.liampwll.com/posts/bend_vibe_coding/
- Bend 2 proof documentation, https://bend2.dev/learn/proofs/
- Comparative coverage discussing Bend 2, SPARK, Lean, and Dafny, https://www.creativeainews.com/articles/bend-2-laws-proof-ai-code-verification-2026/
- Comparative explanation of the Bend/SPARK example, https://elsolitario.org/en/2026/09/18/bend-2-vibe-coding-trap-spark/
