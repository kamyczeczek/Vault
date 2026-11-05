---
type: Concept
id: 243_icm_knowledge_big
title: "ICM_knowledge.md (part 244/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

python3 tools/ask.py -m "prompt" python3 tools/ask.py -m -s "system prompt" "prompt" echo "long prompt" | python3 tools/ask.py -m --stdin python3 tools/ask.py -m gemini --video clip.mp4 "prompt"

Fast, file access via Agent tool

Best Claude coder below Opus, file access

Structured output, native video, different perspective

128k context, fast, cheap

Extended reasoning mode

Single agentic loop

Up to 100 parallel sub-agents, research

Sonnet-adjacent on SWE-Pro/MLE, cheap; use via

mmx_claude.sh

for file tasks

Local Ollama

26B MoE, 256k context, multimodal

gemma-small

Local Ollama

4B, fast lightweight

Choosing the Right Model

#### For code — decision tree:

Is it a one-line edit / rename / format? →

via Agent tool.

Anything bigger that needs file access? →

mmx_claude.sh

(the default).

Did M2.7 escalate with BLOCKED or NEEDS_GUIDANCE on a design question? →

via Agent tool, with the decision baked in.

Is it pure text / research / second opinion / video? →

Video Analysis (Gemini)

#### Gemini natively accepts video — no frame extraction needed. Use it for:

Reviewing edits and rough cuts

Generating scene descriptions and shot lists

Content review before posting

Analyzing pacing, transitions, color grading

Extracting spoken content from clips

# Describe what happens in a video

python3 tools/ask.py -m gemini --video clip.mp4 "Describe each scene, noting camera movement, subjects, and mood"

# Review an edit

python3 tools/ask.py -m gemini --video rough_cut.mp4 "Review this edit for pacing. Note any cuts that feel too fast or too slow. Suggest improvements."

# Generate a shot list

python3 tools/ask.py -m gemini --video footage.mov "Create a timestamped shot list with scene descriptions, shot types, and any visible text"

# Content review for social

python3 tools/ask.py -m gemini --video reel.mp4 "Is this suitable for Instagram? Check for: visual quality, pacing for mobile, hook in first 3 seconds, any issues"

The video is uploaded to Gemini's Files API, processed server-side, then deleted after analysis. No frame extraction, no local vision model — Gemini sees the actual video with full temporal understanding.

Kimi Agent Swarm

Kimi K2.5 has a native agent swarm mode — the model automatically decomposes a task, spawns up to 100 parallel sub-agents, executes up to 1,500 tool calls, and aggregates the results. No framework needed — it's model-native.

#### When to use it:

Complex research or analysis tasks that benefit from parallel decomposition. The swarm is automatic — you give it a hard problem and it figures out how to parallelize.

Multi-source research and synthesis

Complex analysis that can be decomposed

Tasks where you'd otherwise dispatch 5+ separate ask.py calls

Broad exploration before you narrow down

#### Not good for:

Tasks that need file access (swarm can't touch your filesystem)

Tasks where you need to control the decomposition (it's automatic)

Simple questions (overkill — use

instant mode)
