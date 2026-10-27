---
type: Concept
title: references
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# References — Scar Efficacy and Typed Interfaces

<!-- Primary sources here are the workspace's own stores (first-party
     measurements); external sources carry over from the prior record
     where their claims are load-bearing here. -->

## First-party (measured this session, 2026-09-06 00:44–01:02Z)

- `.jcode/session-state/failure_ledger.jsonl` — 391 entries; 135
  baseline (retro 09-03/09-04) + 256 live. Measured: per-day, per-tool,
  class taxonomy (7-pass probe series `_dbg_evidence_pack1–7.py`,
  `_dbg_direction_probe1–4.py`, preserved in session-state).
- `.jcode/session-state/dispositions.jsonl` — 396 dispositions
  (135 baseline / 257 benign / 4 problem); same-day rate 252/391=64%.
- `brains/reflection_brain/reflection_index.json` — 76 scars, 45
  reflections, 64 owning docs; scar-birth sessions per class.
- `brains/reflection_brain/digest.md` — 12,616 chars; overlay injected
  block ~1,675 tokens (gen_digest output 2026-09-06).
- Prior-record claims ledger
  (`../2026-09-05_antifragile-workspace-design/claims_ledger.md`) —
  A3 (typed-slot failure routing), B3 (Memento HLE +116.2%), D3
  (mechanism-over-instruction), F1/F2 (SkillOpt validation-gated
  edits, 52/52 cells) — the external-claim basis this record's §1/§4
  build on.

## External (carried from prior record, unchanged)

- NVIDIA workspace-optimization / DREAMTEAM (Workspace_Optimization.pdf,
  archived in prior record sources/) — typed-slot credit assignment.
- Memento-Skills (Memento-Skills Let Agents Design Agents.pdf, prior
  sources/) — skills-as-memory training gains.
- SkillOpt (skillopt.txt, prior sources/) — validation-gated skill-doc
  editing under benchmark budget.
- OpenAI Agents SDK Memory docs (saved page, prior sources/) — two-phase
  consolidation pattern.
- ICM paper + Atomic Agents (ICM_map.md / Atomic Agents... .md, prior
  sources/) — state-is-folder, blind dispatcher doctrine.
- Practitioner corpus (Rituals..., Stopping Conflicting Saves..., etc.,
  prior sources/) — adversarial verification, intent-first chains.

## Method note

All first-party numbers computed by file-based probes (never `python -c`
— its own trap class is a subject of this record, observed live twice
during the probe series: probes were written to disk then run).
