---
type: Concept
title: SkillOpt
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Structured Notes — `skillopt.txt` (Microsoft SkillOpt Repository Analysis)

## 1. Overview

**SkillOpt** is a Microsoft Research framework that treats a natural-language **skill document** as the trainable state of a frozen agent. Instead of fine-tuning model weights, it iteratively improves a Markdown skill file through:

- **Rollouts** — target model executes tasks with the current skill.
- **Reflection** — optimizer model analyzes trajectories and proposes bounded edits.
- **Aggregation** — merges candidate edits.
- **Selection** — ranks and clips edits (textual learning rate).
- **Update** — applies edits to produce a candidate skill.
- **Gate** — accepts/rejects the candidate based on a held-out validation score.

Two complementary workflows exist:

| Workflow                     | Package / command                             | Purpose                                                      |
| ---------------------------- | --------------------------------------------- | ------------------------------------------------------------ |
| **Research engine**          | `skillopt`, `skillopt-train`, `skillopt-eval` | Train/evaluate skills on benchmark splits.                   |
| **SkillOpt-Sleep (preview)** | `skillopt_sleep`, `skillopt-sleep`            | Nightly offline self-evolution for local coding agents using real session data. |

The repository contains 435 files, estimated 1.1M tokens.

---

## 2. Key Results & Claims

### Research Engine (SkillOpt)
- Best or tied-best on **all 52 evaluated (model, benchmark, harness) cells**.
- GPT-5.5 average no-skill accuracy lift:
  - **+23.5 points** in direct chat
  - **+24.8 points** inside Codex agentic loop
  - **+19.1 points** inside Claude Code
- Optimized skills **transfer** across model scales, between Codex and Claude Code harnesses, and to nearby benchmarks.
- Six benchmarks, seven target models, three execution harnesses tested.

### SkillOpt-Sleep
- Nightly offline self-evolution: harvest past sessions → mine recurring tasks → replay offline → consolidate behind held-out gate → stage proposal → user adopts.
- Validation gate prevents catastrophic regressions: in a stress test, ungated run collapsed from **55.4% → 2.6%**; gated run stayed flat at **57.0%**.
- GPT-5.4-nano on SearchQA: **+11.9 points** (0.560 → 0.679) over 5 nights.
- SpreadsheetBench (GPT-5.4-nano): **+3.6 points**.
- gbrain-evals `skillopt-v1`: deficient skills go **0.00 → 1.00** on held-out tasks with both Claude Code and Codex.

---

## 3. Repository Structure (Top-Level)

```
microsoft-skillopt/
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE (MIT)
├── pyproject.toml
├── mkdocs.yml
├── configs/                  # YAML configs per benchmark
├── data/                     # Split manifests (ID/path only)
├── docs/                     # Full documentation
├── plugins/                  # Agent integrations (Claude Code, Codex, Cursor, etc.)
├── scripts/                  # train.py, eval_only.py, materializers
├── skillopt/                 # Research engine package
├── skillopt_sleep/           # SkillOpt-Sleep package
├── skillopt_webui/           # Gradio dashboard
├── tests/                    # Extensive test suite
└── ckpt/                     # Paper-aligned reference skills
```

---

## 4. Core Concepts

### Skill Document
- Markdown file acting as “prompt weights”.
- Evolves via **add / delete / replace** edits.
- Protected regions:
  - `<!-- SLOW_UPDATE_START -->` … `<!-- SLOW_UPDATE_END -->`
  - `<!-- APPENDIX_START -->` … `<!-- APPENDIX_END -->`
- Step-level edits cannot modify protected regions.

### Training Loop (Deep Learning Analogy)
| DL Concept        | SkillOpt Equivalent                       |
| ----------------- | ----------------------------------------- |
| Model weights     | Skill document                            |
| Forward pass      | Rollout                                   |
| Loss/gradient     | Reflect (edit patches)                    |
| Gradient clipping | Edit selection (`learning_rate`)          |
| SGD step          | Apply patch                               |
| Validation set    | Selection split / gate                    |
| Epoch             | Multi-epoch with slow update & meta skill |

### Slow Update
- Epoch-level longitudinal comparison between previous and current skill on same tasks.
- Writes durable guidance into protected `SLOW_UPDATE` region.
- Can be gated on selection split or force-accepted.

### Meta Skill
- Optimizer-side memory accumulated across epochs.
- Helps future reflection/aggregation/ranking.

### Skill-Aware Reflection (EmbodiSkill)
- Routes failures into:
  - **SKILL_DEFECT** → body edit
  - **EXECUTION_LAPSE** → protected appendix note
- Toggle: `optimizer.use_skill_aware_reflection`
- Appendix source: `both` or `failure_only`
- Optional consolidation threshold.

### Validation Gate
- Pure decision function: `evaluate_gate`, `select_gate_score`.
- Metrics: `hard`, `soft`, `mixed`.
- `use_gate: true` (default) — accept only strict improvement.
- `use_gate: false` — force-accept, but validation still recorded.
- `gate_no_regression` — reject any candidate that lowers a validation task score.

---

## 5. Research Engine Components

### `skillopt/`
- **`engine/trainer.py`** — `ReflACTTrainer`, main loop.
- **`envs/`** — benchmark adapters: SearchQA, DocVQA, ALFWorld, OfficeQA, LiveMathematicianBench, SpreadsheetBench.
- **`gradient/`** — `reflect.py` (minibatch reflection), `aggregate.py` (hierarchical merge).
- **`optimizer/`** — `clip.py` (rank/select), `slow_update.py`, `meta_skill.py`, `skill_aware.py`, `update_modes.py`.
- **`evaluation/gate.py`** — validation gate.
- **`model/`** — backend router and backends.
- **`datasets/base.py`** — `BaseDataLoader`, `SplitDataLoader`, `BatchSpec`.
- **`types.py`** — `Edit`, `Patch`, `RolloutResult`, `RawPatch`, `SlowUpdateResult`, `GateResult`.

### Supported Backends
| Backend             | Optimizer | Target | Notes                              |
| ------------------- | --------- | ------ | ---------------------------------- |
| `openai_chat`       | ✓         | ✓      | Azure OpenAI + auth modes          |
| `openai_compatible` | ✓         | ✓      | Generic OpenAI-compatible endpoint |
| `claude_chat`       | ✓         | ✓      | Claude Code CLI (`claude -p`)      |
| `qwen_chat`         | ✓         | ✓      | Qwen via OpenAI-compatible server  |
| `minimax_chat`      | ✓         | ✓      | MiniMax API                        |
| `copilot_chat`      | ✓         | ✓      | GitHub Copilot CLI                 |
| `codex_exec`        | ✓         | ✓      | Codex CLI execution harness        |
| `claude_code_exec`  | ✓         | ✓      | Claude Code CLI execution harness  |
| `cursor_exec`       | —         | ✓      | Cursor Agent CLI harness           |
| `copilot_exec`      | —         | ✓      | GitHub Copilot CLI harness         |

### Benchmarks
- **SearchQA** — open-domain QA, SQuAD exact-match.
- **DocVQA** — document image QA.
- **ALFWorld** — embodied household tasks.
- **OfficeQA** — enterprise document retrieval QA.
- **LiveMathematicianBench** — math MCQ.
- **SpreadsheetBench** — spreadsheet manipulation (openpyxl code execution).

Each has:
- Adapter
- Dataloader
- Rollout
- Evaluator
- Prompts
- Initial skill

### Training Artifacts
```
outputs/<run>/
├── config.json
├── runtime_state.json
├── history.json
├── best_skill.md
├── skills/skill_vXXXX.md
├── steps/step_XXXX/
│   ├── candidate_skill.md
│   ├── step_record.json
│   ├── ranked_edits.json
│   └── trajectory_digest.json
├── slow_update/epoch_XX/
└── meta_skill/epoch_XX/
```

### CLI
- `skillopt-train` / `python scripts/train.py`
- `skillopt-eval` / `python scripts/eval_only.py`
- Common flags: `--config`, `--cfg-options`, `--backend`, `--optimizer_model`, `--target_model`, `--out_root`, `--split`, `--skill`.

---

## 6. SkillOpt-Sleep (Deployment Companion)

### Purpose
Nightly offline self-evolution for a local coding agent. Uses real session transcripts to mine recurring tasks, replay them, and consolidate validated updates into memory (`CLAUDE.md`) and skills (`SKILL.md`).

### Cycle
```
harvest → mine → replay → consolidate (gated) → stage → adopt
```

### Sources
- Claude Code transcripts (`~/.claude/projects`)
- Codex Desktop archived sessions
- VS Code GitHub Copilot Chat
- Copilot CLI session store
- Cursor Agent transcripts
- Pi sessions
- OpenCode SQLite history

### Backends
`mock`, `claude`, `codex`, `copilot`, `cursor`, `pi`, `opencode`, `handoff`, `azure_openai`.

### Safety
- **Read-only harvest**.
- **Staged proposals** — nothing live changes until `adopt`.
- **Backups** on adoption.
- **Secret redaction** before persisting diagnostics/evidence.
- **Validation gate** prevents regressions.
- `mock` and `handoff` make no network calls.

### Key Config Options
- `gate_mode`: `on` / `off`
- `gate_metric`: `hard` / `soft` / `mixed`
- `gate_no_regression`
- `dream_rollouts`: >1 for contrastive reflection
- `dream_factor`: synthetic variants
- `recall_k`: associative recall of past tasks
- `evolve_skill` / `evolve_memory`
- `preferences`: free-text house rules
- `multi_skill_fanout`: per-skill proposals

### Multi-Skill Staging
- Each hinted skill gets its own proposal file and gate result.
- `adopt --skill NAME`, `--all-skills`, or `--legacy`.
- Versioned manifest with SHA-256 pins, live baseline hashes, transaction journal, rollback.

### Plugins
| Platform         | Mechanism                                  |
| ---------------- | ------------------------------------------ |
| Claude Code      | marketplace plugin, commands, hooks, skill |
| Codex            | user-level skill + runner                  |
| Cursor           | native command/skill + runner              |
| Copilot          | MCP server (`sleep_*` tools)               |
| Devin            | MCP server + transcript converter          |
| DeepSeek Harness | Cordis plugin (`skillopt_*` tools)         |
| OpenClaw         | reference adaptation                       |

### CLI
```
skillopt-sleep run | dry-run | status | adopt | harvest | schedule | unschedule | evalkit
```
Common flags: `--project`, `--scope`, `--backend`, `--source`, `--model`, `--max-sessions`, `--max-tasks`, `--target-skill-path`, `--tasks-file`, `--preferences`, `--auto-adopt`, `--json`.

---

## 7. WebUI

- Gradio dashboard: `python -m skillopt_webui.app`
- Flags: `--port` (default 7860), `--host` (default `0.0.0.0`), `--share`.
- Configure, launch, and monitor training from browser.

---

## 8. Configuration

- Structured YAML with `_base_` inheritance.
- Sections: `model`, `train`, `gradient`, `optimizer`, `evaluation`, `env`.
- CLI overrides via `--cfg-options section.key=value`.
- Environment variables for credentials:
  - `AZURE_OPENAI_*`
  - `OPENAI_COMPATIBLE_*`
  - `CLAUDE_CLI_BIN`, `ANTHROPIC_API_KEY`
  - `QWEN_CHAT_*`
  - `MINIMAX_*`
  - `COPILOT_*`
  - `CURSOR_EXEC_*`
- Per-role overrides: `OPTIMIZER_*`, `TARGET_*`.

---

## 9. Data & Manifests

Six benchmark split manifests under `data/`:

| Manifest               | Counts (train/val/test) | Raw source                            |
| ---------------------- | ----------------------- | ------------------------------------- |
| SearchQA               | 400 / 200 / 1400        | HF `lucadiliello/searchqa`            |
| LiveMathematicianBench | 35 / 17 / 125           | HF LiveMathematicianBench             |
| DocVQA                 | 107 / 53 / 374          | HF `lmms-lab/DocVQA` (10% validation) |
| OfficeQA               | 50 / 24 / 172           | HF `databricks/officeqa`              |
| SpreadsheetBench       | 80 / 40 / 280           | HF `KAKA22/SpreadsheetBench`          |
| ALFWorld               | 39 / 18 / 134           | ALFWorld `json_2.1.1` paths           |

Manifests are **ID-only** or **path-only**; full payloads must be materialized separately (e.g., `scripts/materialize_searchqa.py`).

---

## 10. Checkpoints

`ckpt/` contains paper-aligned GPT-5.5 optimized skills for:
- SearchQA
- ALFWorld
- DocVQA
- LiveMathematicianBench
- OfficeQA
- SpreadsheetBench

Each is a Markdown skill document (~2k–13k chars) with a protected `SLOW_UPDATE` section.

---

## 11. Testing & Quality

- `tests/` — extensive pytest suite covering backends, gates, harvesters, staging, consolidation, multi-skill, WebUI, security.
- `ruff` for linting, `mkdocs` for docs.
- Contributing guide: `CONTRIBUTING.md`, `docs/contributing.md`, `docs/review_guidelines.md`.
- Security policy: `SECURITY.md`.

---

## 12. Key Differentiators

- **No weight training** — purely text-space optimization.
- **Validation gate** — prevents regressions; can be disabled but not recommended.
- **Bounded edits** — textual learning rate controls change size.
- **Slow update & meta skill** — long-horizon stability.
- **Cross-model transfer** — learned skill works on different models/harnesses.
- **SkillOpt-Sleep** — applies same discipline to real daily agent usage.
- **Extensive plugin ecosystem** — Claude Code, Codex, Cursor, Copilot, Devin, DSH, OpenClaw.
- **Safety-first design** — staged proposals, backups, redaction, read-only harvest.

---

## 13. Citation

```bibtex
@article{yang2026skillopt,
  title={Skillopt: Executive strategy for self-evolving agent skills},
  author={Yang, Yifan and Gong, Ziyang and Huang, Weiquan and Yang, Qihao and Zhou, Ziwei and Huang, Zisu and Li, Yan and Gao, Xuemei and Dai, Qi and Liu, Bei and others},
  journal={arXiv preprint arXiv:2605.23904},
  year={2026}
}
```

---

## 14. Quick Start Summary

**Research engine:**
```bash
pip install -e ".[searchqa]"
python scripts/materialize_searchqa.py
python scripts/train.py --config configs/searchqa/default.yaml
python scripts/eval_only.py --config configs/searchqa/default.yaml \
  --skill outputs/<run>/best_skill.md --split valid_unseen
```

**SkillOpt-Sleep:**
```bash
pip install skillopt
skillopt-sleep dry-run
skillopt-sleep run
skillopt-sleep status
skillopt-sleep adopt
```

**WebUI:**
```bash
pip install -e ".[webui]"
python -m skillopt_webui.app
```