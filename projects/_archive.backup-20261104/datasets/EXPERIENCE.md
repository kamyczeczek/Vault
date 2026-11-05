---
type: Concept
title: EXPERIENCE
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# EXPERIENCE.md — datasets

Distilled on demand 2026-09-27 from `CLAUDE.md`, `CONTEXT.md` (Open work §1–10).
Each lesson names its evidence. Root links here (D11).

## Verified practices

1. **Never commit a dataset; re-fetch it.** `data/*.csv`, `INBOX/` gitignored.
   A consumer runs the fetcher. Evidence: `CLAUDE.md` Rules.
2. **A synthetic series must be labeled synthetic or dropped.**
   An unlabeled generated series inside a "real" catalog invalidates every
   comparison built on it. Evidence: `CLAUDE.md` Rules; Open work §5
   (`Solar_Activity_SIDC`, `Weather_Temperature_Realistic` carry real-source
   names over generated rows), §6 (stock fallback returns invented GBM path
   with console-only notice).
3. **A fetcher records source URL + retrieval date + units + sampling rate.**
   Three of four fields missing in the `results/*.json` metadata writes
   (`source` = series name, no date/units/rate). Evidence: Open work §3.
4. **Public functions are an interface: test them here, not in the sibling.**
   `get_*_data()` imported by three `benchmark-core` scripts; no test in this
   project, so a rename surfaces as `ImportError` elsewhere. Evidence:
   `CLAUDE.md` Dependencies; Open work §8.
5. **Create the directory you write into.**
   Three scripts write `results/<file>.json`; `results/` never created —
   `FileNotFoundError` after the CSVs already landed (partial success reported
   as failure). Evidence: Open work §3.
6. **Pin upstream layout, not filenames.**
   `fetch_etth1.py` requests `ETT.csv` (dead 404; upstream is now
   `ETT-small/ETTh1.csv`) and writes only `date,OT`, dropping the six load
   columns the canonical loader needs. Evidence: Open work §4.
7. **Fallbacks must be visible in the return, not the console.**
   Yahoo `v7/finance/download` now 401s, so the "rare" synthetic fallback is
   the only path — and it is indistinguishable downstream. Evidence: Open
   work §6. Same shape in §2 (`except: continue` → `NaN`/`FAILED` conflates
   broken with unfittable).
8. **Never write into a sibling project without a dry-run flag.**
   `fix_corpus_source.py` rewrites 10k+ corpus files with a four-dash fence
   no YAML parser accepts. Evidence: Open work §10.

## Known-unresolved

- §1: "scientific" fetchers are `np.random` generators with real-source
  citations; fix is breaking for three `benchmark-core` callers — stage it.
- §2: `benchmark_scientific_datasets.py` imports a `members/` that does not
  exist here; no number from it was ever produced.
- §5: nine non-ETT CSVs are orphans (no date column, no sidecar, no
  reproducible generator path).
- §7: `search_datasets_kg.py` needs gitignored `.brain/graph/graph.db`
  (Windows-only path) — dead on fresh clone.
- §9: INBOX readers point at moved paths, walk `C:\Users\Mateusz`, embed
  90-char literals; cited `AGENTIC_DISCOVERY.md` is not in this project.

## Skills used

None vendored (D8 lazy).
