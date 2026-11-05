---
type: Concept
title: world_models_long_horizon_web_research
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# World Models for Long-Horizon Agent Planning

## Core concepts

World models are internal representations that let an agent predict future states and evaluate plans without executing every action. For long-horizon tasks, they reduce branching by reasoning over imagined trajectories instead of retrying real actions. Key design points: the model must predict action outcomes, support counterfactual planning, and ground predictions in observed evidence rather than parametric priors.

## Evidence from web sources

- DreamerV3 and Genie-style world models scale to diverse environments by learning compressed latent dynamics. They outperform model-free baselines on long-horizon reward because the agent can "see" outcomes before acting. Limitations: sim-to-real gap, compounding prediction errors over long rollouts, and high compute cost for model training.
- LLM-based planning with world-model rollouts (e.g., Tree of Thoughts, Language Model Cascades) uses the model itself as the world simulator for text environments. Strengths: no separate model training. Weaknesses: hallucinated dynamics, no external verification, which maps to the grounding failure mode already in corpus (`00_06_self_correction_grounding_requirement`).
- Grounded world models attach an external verifier (unit tests, API responses, environment feedback) to each rollout. This matches CRITIC's verify-then-correct loop and is the only form that measurably improves long-horizon success. Without grounding, imagined trajectories degrade exactly like intrinsic self-correction.

## Why it matters for this workspace

The ICM pipeline is itself a lightweight world model for knowledge work: corpus state → graph digest → reflection candidate → eviction decision. The gap today is that rollout is implicit and not externally verified beyond manifest and graph checks. Adding explicit counterfactual stage-gate checks would strengthen prediction before action.

## Source

Web research: agent world model planning, DreamerV3, LLM rollouts, grounded verification.
