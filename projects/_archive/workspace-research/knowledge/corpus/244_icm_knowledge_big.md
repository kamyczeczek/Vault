---
type: Concept
id: 244_icm_knowledge_big
title: "ICM_knowledge.md (part 245/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Research task

python3 tools/ask.py -m kimi-swarm "Research the current state of OFX plugin development for DaVinci Resolve. Cover: available frameworks, Metal vs CUDA support, plugin distribution, licensing models, and any open-source examples."

# Analysis task

python3 tools/ask.py -m kimi-swarm "Analyze the competitive landscape for AI-powered colour grading plugins. Compare features, pricing, and user reviews across all major options."

# Extended reasoning (single agent, not swarm)

python3 tools/ask.py -m kimi-think "Given these constraints [paste constraints], what architecture would you recommend and why?"

#### Kimi modes quick reference:

| Mode | Flag | Use case | Speed |

|------|------|----------|-------|

| Instant |

| Simple questions, fast drafts | Fast |

| Thinking |

| Complex reasoning, analysis | Moderate |

| Single-thread agentic task | Slow |

| Parallel decomposition, research | Slowest (but most thorough) |

Default to M2.7 via

mmx_claude.sh

for code tasks.

Fall back to

(Agent tool) only for trivial one-liners, and escalate to

(Agent tool) only when M2.7 hits a design ambiguity. Use

for pure text, research, second opinions, or local/free generation via

Local Models (Ollama — free, private, offline)

Gemma 4 (26B MoE) runs locally on this Mac (M1 Max, 64GB). No API key, no cost, no data leaves the machine.

# General text generation

python3 tools/ask.py -m gemma "Draft 3 caption options for this photo: [description]"

# Fast lightweight tasks

python3 tools/ask.py -m gemma-small "Reformat this JSON: {raw json}"

Good for: drafts, reformatting, classification, simple analysis, privacy-sensitive content, offline work, bulk generation where API costs would add up.

Not good for: complex reasoning (use kimi-think or sonnet), tasks needing current web knowledge (use gemini or kimi-swarm).

Checking for questions (do this on every turn)

Background workers surface decisions through file-based questions. The main

Opus session must check for them at the start of each response generation.

#### Convention (not enforced, but load-bearing):

python3 tools/dispatch.py questions

before your first real action in each turn

whenever you have

live background workers. If the output is

(no unresolved questions)

normally. If it contains one or more worker question blocks, surface them to

#### Ari near the top of your response using this shape:

## 🛎️ Background worker questions

### w-a3f2-impl-foo (executor=minimax)

task: Implement /api/foo endpoint per spec.md where stuck: JWT vs random hex — both patterns exist in this codebase

**Question:** Which token format should the reset flow use?

**What would unblock:** One of "jwt" or "hex", with a one-line reason if the choice affects how I wire up the lookup.

Surfacing rules (non-negotiable)

Queue per turn, never mid-message.

If a question surfaces between

responses, don't jam it into the message you're already writing. Show it

Group by worker.
