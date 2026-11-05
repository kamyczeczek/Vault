---
type: Concept
id: planning-with-files-pattern
title: "Planning with Files: task_plan + findings + progress on Disk, Hooks as Re-injection"
source: "othmanadi/planning-with-files (GitHub, 698 files, 2M tokens, 60+ agents, Manus-style) + Jina"
tags: [planning, icm, planning-with-files, hooks, determinism, long-running, context-engineering, agents]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Manus-style working memory on disk: three files per task — task_plan.md (phases+checkboxes, resume after /clear), findings.md (research), progress.md (session log). Isolated .planning/YYYY-MM-DD-slug/ with .active_plan for parallel. Principle: Context Window=RAM volatile, Filesystem=Disk persistent. Auto hooks re-inject plan head every turn (5 Claude Code, 7 Codex, 8 Pi); SessionStart/UserPromptSubmit/PreCompact carry current phase; Stop gate + SHA-256 attestation [PLAN TAMPERED] + parallel-write guard + /plan-doctor (706 tests, 96.7% pass, 3/3 A/B wins). ICM alignment: filesystem-as-memory already via WORKFLOW.md/stages; add per-turn re-injection and attestation alongside watch.py fingerprint + gates.
