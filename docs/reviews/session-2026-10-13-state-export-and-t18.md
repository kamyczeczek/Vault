# Session Report: 2026-10-13 — State Export + T18 Family-Aware Refusal

**Owner:** agnes-2.5-flash
**Agent:** agentic-session
**Phase:** Faza 1 + Faza 2 (T18)

## TL;DR
1. **Faza 1 (State Export):** Implemented deterministic workspace state export using repomix. Added `repomix.config.json` with security checks, created `handoff/state_description/CONTEXT.md`, and updated `CLAUDE.md` routing. Walk test passed — cold agent finds state within ≤2 reads.
2. **Faza 2 (T18):** Changed refusal policy in `graphrag.py` from exact-ID to family-aware. Added `family_recall@5` metric. False refusals ↓44% (48.5% → 27.3%), no OOC regression.

## Phase 1: State Export

### Changes
- Created `repomix.config.json` — includes CLAUDE.md, AGENTS.md, SCARS.md, docs/, handoff/flags/, scripts/*.py; excludes node_modules, projects/**, *.db
- Created `handoff/state_description/CONTEXT.md` — ≤30 line ICM-style summary
- Updated `CLAUDE.md` — added routing row: `handoff/state_description/`
- Ran `npx repomix --config repomix.config.json` — processed 187 files
- Verified secrets clean: `python scripts/scan_secrets.py handoff/state_description/txt_files/workspace-state.txt`

### Evidence
```
npx repomix --config repomix.config.json
→ 187 files processed
python scripts/scan_secrets.py handoff/state_description/txt_files/workspace-state.txt
→ SECRETS_CLEAN
```

### Walk Test
Cold agent reads `CLAUDE.md` → finds routing row within first ~30 lines → opens `handoff/state_description/CONTEXT.md` → reads ICM summary. Done in ≤2 reads.

## Phase 2: T18 — Family-Aware Refusal

### Problem (from T13)
88.9% of false refusals are family-match-only: retriever finds correct book in top-5, but system refuses because keyword coverage checked against wrong chunk.

### Changes Made
1. **`graphrag.py`** — Added `family_recall_at_k()` function (slug-level recall, strips `NN_` prefix)
2. **`graphrag.py`** — Modified `syntezuj_odpowiedz()`: when `n_pokrytych == 0`, fallback to family-aware check before hard refusal
3. **`measure_trust_set.py`** — Added `family_recall@5` column to output and JSON

### Code Diff
```diff
+# family_recall_at_k — Recall@k na slugach (bez prefiksu NN_)
+def family_recall_at_k(oracle_ids: list[str], ranked_ids: list[str], k: int = 5) -> float:
+    gold_slugs = {o.split("_", 1)[1] for o in oracle_ids if "_" in o}
+    retrieved_slugs = {r.split("_", 1)[1] for r in ranked_ids[:k] if "_" in r}
+    return len(gold_slugs & retrieved_slugs) / len(gold_slugs) if gold_slugs else 0.0

 # In syntezuj_odpowiedz, when n_pokrytych == 0:
+    # Zmiana 2: family-aware refusal (fallback)
+    potential_family_matches = [c for c in pokryte if c["source_family"] and c["n_trafien"] > 0]
+    if potential_family_matches:
+        return {"odpowiedz": "...family match...", "odmowa": False, "family_match": True}
```

### Results

| Metric | Baseline (T13) | After T18 | Δ |
|--------|---------------|-----------|---|
| FALSE REFUSAL (in-corpus) | 48.5% | **27.3%** | **↓44%** |
| OOC refusal | 66.7% | 66.7% | 0% |
| family_recall@5 | — | **93.9%** | new metric |

### Tool Calls Evidence
```bash
cd projects/research/knowledge-retrieval/pilots/graphrag/eval
python measure_trust_set.py
→ FALSE REFUSAL in-corpus (n=33): 27.3%
```

```bash
python -c "import json; d = json.load(open('trust_set_results.json')); inc = [r for r in d if r['typ']=='in-corpus']; print(f'family_recall@5 avg: {sum(r.get(\"family_recall@5\",0) for r in inc)/len(inc):.3f}')"
→ family_recall@5 avg: 0.939
```

## Decisions

1. **Family-aware refusal (not lowering MIN_KEYWORD_MATCHES):** Changing global threshold would risk OOC breach (kr-stage-isolation showed 50% boundary leaks at lower thresholds). Family-aware fallback is safer — still emits `family_match=True` with low confidence when only family-level match found.

2. **`family_recall@5` strips `NN_` prefix:** Slug comparison uses `split("_", 1)[1]` on both oracles and ranked IDs, computing family-level recall independent of node instance IDs.

## Next Steps
- Continue monitoring false refusal rate in subsequent sessions
- Consider lowering family-match confidence threshold if false refusals still high
- T19: Investigate remaining 27.3% false refusals — are they boundary cases or pure retrieval failures?

---
*Report written by agnes-2.5-flash. All numbers verified by tool calls in this session.*
