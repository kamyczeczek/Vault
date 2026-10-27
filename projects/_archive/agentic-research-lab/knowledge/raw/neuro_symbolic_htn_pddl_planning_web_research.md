---
type: Concept
title: neuro_symbolic_htn_pddl_planning_web_research
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Neuro-Symbolic HTN and PDDL Planning with Language Models

## Core concepts

Hierarchical Task Network (HTN) planning and PDDL (Planning Domain Definition Language) provide formal symbolic guarantees on plan correctness and goal reachability. Pure LLM generation suffers from hallucinations, incomplete pre-condition checking, and illegal state transitions. Integrating approximate LLM generation with symbolic HTN/PDDL solvers combines the commonsense reasoning of foundation models with the soundness and verification guarantees of classical planners.

## Evidence from web sources

- **ChatHTN: Interleaving Approximate (LLM) and Symbolic HTN Planning (Muñoz-Avila, Aha, Rizzo, PMLR v288, 2025):** Combines symbolic HTN planning with ChatGPT task decomposition queries. Even though LLM suggestions are approximate, ChatHTN proves sound: every synthesized plan is formally verified by the symbolic HTN verifier to guarantee it achieves the input goals.
- **ProcLLM: Procedural Knowledge Improves Agentic LLM Workflows (DOI 10.65109/vevz5917, 2026):** Incorporating formal procedural schemas into LLM reasoning loops eliminates aimless branching and enforces domain-specific invariants.
- **PDDLEGO: Iterative Planning in Textual Environments (*SEM 2024):** Translates informal agent intentions into modular PDDL goals and actions, verifying action preconditions against environment state before execution.
- **L2HP & HPlan (ICAPS 2025 Roadmap, arXiv 2501.08068):** General framework for learning and grounding hierarchical planning representations with LLMs.
- **Online Learning of HTN Methods (arXiv 2511.12901) & Hive (arXiv 2412.12839):** Continual refinement of HTN decomposition methods from execution feedback, enabling the agent to learn reusable decomposition patterns over time.

## Why it matters for this workspace

This provides the formal theoretical foundation for ICM stage decomposition and `route.py` alias splitting (`decomposition/htn/pddl/classical-planning`):
1. Top-level plans provide high-level task networks.
2. Individual stages act as compound tasks reduced to primitive operator scripts (`check_*.py`, `ingest.py`, `build_graph.py`).
3. Interleaving deterministic gates with LLM generation guarantees end-to-end soundness while retaining agent flexibility.

## Source

web: https://proceedings.mlr.press/v288/munoz-avila25a.html + https://doi.org/10.65109/vevz5917 + https://aclanthology.org/2024.starsem-1.17v2.pdf + https://arxiv.org/abs/2501.08068 + https://arxiv.org/html/2511.12901
