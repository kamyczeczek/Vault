---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Stage 01_inbox — Intake and Raw Manifest Staging

Intake boundary for raw research notes, literature summaries, and seed papers deposited into `INBOX/`.

## Inputs
- `INBOX/` raw markdown notes with frontmatter
- `knowledge/raw/` raw storage directory

## Process
1. Load active heuristics: `python scripts/apply_rules.py --task "inbox intake and source analysis" --format prompt`
2. Inspect `INBOX/` for uningested files.
3. Ensure every note adheres to frontmatter format (`title:`, `source:`, `tags:`).
4. Run `python scripts/ingest.py` to move files to `knowledge/raw/`, chunk into `knowledge/corpus/`, and rebuild `manifest.jsonl`.
## Outputs
- `knowledge/raw/manifest.jsonl` (derived manifest)
## Mandatory In-Depth Technical Analysis Rule
- Intake notes and paper depositions must not be mere summaries; they must outline exact algorithms, data structures, and threat models.

- Emptied `INBOX/` directory

## Exit Gate
- `INBOX/` is completely empty.
- `python scripts/check_manifest.py` exits 0.
- `python scripts/check_research_quality.py` exits 0 before ingestion.

## Evolved Protocol Rule (Mandatory In-Depth Technical Analysis of Sources)
<!-- meta-evolved: Mandatory In-Depth Technical Analysis of Sources -->
- **Origin Evidence:** `,`
- **Requirement:** Ingested scientific papers and GitHub projects must never be reduced to superficial summaries; they must undergo exhaustive technical analysis detailing exact algorithms, data structures, threat models, and architectural boundaries.


## Evolved Protocol Rule (Research depth requires skeletal specification and reusable failure triples, not summaries.)
<!-- meta-evolved: Research depth requires skeletal specification and reusable failure triples, not summaries. -->
- **Origin Evidence:** ``00_don_t_vibe_code_do_skele_code_interactive_no_cod`, `01_09_mistake_correction_abstraction_level`, `00_taxonomy_of_20_ai_research_failure_modes`, `00_agent_error_taxonomy_debugging_web_research`, `00_defensive_failure_mode_hardening``
- **Requirement:** Require every ingested chunk to state architecture primitives, algorithmic mechanisms, and threat model and limitation boundaries with skeletal spec first, then body; record every lesson as a failure condition, reason and correction triple; isolate work, capture before and after proof, and pass independent review before ship.
