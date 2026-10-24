# Raport sesji: Rozstrzygnięcie wąskiego gardła retrievera KR — 2026-10-13

## Weryfikacja poprzedniej sesji
- `git log -1 --format=%B 36a0dff` → `kr-baseline-diagnosis-2026-10-13: kr-baseline-diagnosis-2026-10-13 — 2026-10-13: baseline MRR@5=0.295, false refs=48.5%, hipotez`
- Flaga `kr-baseline-diagnosis-2026-10-13.md` → Pełna treść odczytana w Kroku 0 (baseline MRR@5=0.295, false refs=48.5%, hipoteza o FTS5).
- Raport poprzedniej sesji `docs/reviews/session-2026-10-13-kr-baseline-diagnosis.md` → Przeczytany w całości w Kroku 0.
- **Werdykt:** Czy diagnoza per etap była pozorna? **TAK**. W poprzedniej sesji przypisano te same zbiorcze metryki retrievalu do etapu ranking oraz attribution bez niezależnych pomiarów dla każdego etapu w izolacji.

## Baseline i rozbicie na stopnie
### 1. Baseline (hybryda ON: FTS5 + Wektory RRF)
- **Komenda:** `python projects/research/knowledge-retrieval/pilots/graphrag/eval/measure_trust_set.py`
- **Surowy output zbiorczy:**
  - IN-CORPUS (n=33): Recall@1=0.159, Recall@3=0.417, Recall@5=0.455, Recall@10=0.515, MRR@5=0.295, MRR@10=0.303

### 2. FTS5-only (`uzyj_wektorow=False`)
- **Komenda:** `python scripts/_scratch/run_stage_isolation_krok1.py` (uruchomione przez `run_and_rc.sh`)
- **Surowy output zbiorczy:**
  - IN-CORPUS (n=33): Recall@1=0.098, Recall@3=0.144, Recall@5=0.152, Recall@10=0.182, MRR@5=0.136, MRR@10=0.139

### 3. Wektory-only
- **Komenda:** `python scripts/_scratch/run_stage_isolation_krok1.py` (wektory w izolacji)
- **Surowy output zbiorczy:**
  - IN-CORPUS (n=33): Recall@1=0.250, Recall@3=0.379, Recall@5=0.409, Recall@10=0.500, MRR@5=0.334, MRR@10=0.347

## Hipoteza główna
Recall@10 wynosi 0.515 w baseline, 0.182 w FTS5-only i 0.500 w wektorach-only; różnica między FTS5-only a baseline wynosi 0.333. Wąskie gardło to warstwa FTS5 i dopasowanie słów kluczowych (FTS5 sam w sobie drastycznie odstaje od wektorów), a wektory (oraz fuzja RRF) dostarczają ponad 64% trafności (Recall@10 podskakuje z 0.182 do 0.500/0.515).

## Boundary refusal
- **Surowy fragment `trust_set_results.json` (B01–B10):**
  - B01: odmowa=True (Jak skonfigurować GraphRAG w Kubernetes?)
  - B02: odmowa=True (Czy SEVerA obsługuje PostgreSQL?)
  - B03: odmowa=False (Jak zintegrować agent memory hierarchies z Redis?)
  - B04: odmowa=True (Jaka jest cena licencji na technologię agentforce?)
  - B05: odmowa=False (Jak wdrożyć graph databases w AWS?)
  - B06: odmowa=True (Czy jest dostępny Python SDK dla graphrag?)
  - B07: odmowa=False (Jak monitorować wydajność agent execution hooks?)
  - B08: odmowa=True (Jakie są limity API dla agentic RAG?)
  - B09: odmowa=False (Jak skalować vector index do 1M węzłów?)
  - B10: odmowa=False (Jak zabezpieczyć knowledge graph przed atakami?)
- **Hipoteza druga:** 50% boundary refusals wynika z tego, że pytania boundary zawierają istotne słowa kluczowe z domeny (np. `GraphRAG`, `vector index`, `graph databases`, `agent memory`), które przekraczają próg `MIN_KEYWORD_MATCHES=2` w silniku attribution, powodując fałszywe uznanie pytań out-of-corpus/boundary za in-corpus.

## Next steps (kolejność wg ROI)
1. Kalibracja i oddzielenie polityki odmów (boundary/out-of-corpus) od dopasowania keywordów w in-corpus, aby wyeliminować 50% false positives na boundary przy jednoczesnym obniżeniu 48.5% false refusals.
2. Wzmocnienie modułu FTS5 przez synonimizację i ekstrakcję pojęć, ponieważ czysty FTS5 ma Recall@10 zaledwie 0.182.
3. Ręczna kwalifikacja 18 pytań w buckecie ZAWODNE.

## not checked:
- `_tmp_*` pliki tymczasowe w `scripts/_scratch/` (w tym `krok1_results.json`, `run_stage_isolation_krok1.py`, `inspect_boundary.py`).
- Ręczna kwalifikacja 18 pytań ZAWODNE pod kątem poprawności goldów.

## R18 / governance
Ta sesja jest badawcza. Governance streak zamknięty w `workflow-verification-fix-2026-10-13`. Nie otwarto nowej warstwy governance.

## Git Commit Log (po close.py)
```
kr-stage-isolation-2026-10-13: `kr-stage-isolation-2026-10-13` — 2026-10-13: baseline Recall@10=0.515, FTS5-only Recall@10=0.182. Wąskie gardło: FTS5 (wektory dają Recall@10=0.500). Boundary: 50% przepuszcza.
```
