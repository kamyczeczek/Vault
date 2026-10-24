# Raport sesji: Odchudzenie retrievera KR i dodanie sprawdzonego ROI — 2026-10-13

## Baseline vectors-only (Krok 1)
- **Komenda:** `python scripts/_scratch/run_stage_isolation_krok1.py`
- **Surowy output zbiorczy:**
  - `[VECTORS_ONLY] n=33: Recall@1=0.250, Recall@3=0.379, Recall@5=0.409, Recall@10=0.500, MRR@5=0.334, MRR@10=0.347`

## Cross-encoder reranking (Krok 2)
- **Komenda:** `python scripts/_scratch/run_rerank.py`
- **Surowy output zbiorczy:**
  - `[VECTORS_RERANK (BAAI/bge-reranker-base)] n=33: Recall@1=0.303, Recall@3=0.409, Recall@5=0.470, Recall@10=0.530, MRR@5=0.376, MRR@10=0.384`
- **Delta MRR@5:** 0.334 → 0.376 (+0.042)

## Metadata filtering (Krok 3)
- **Komenda:** `python scripts/_scratch/run_metadata_filter.py`
- **Surowy output zbiorczy:**
  - `[METADATA_FILTER] n=33: Recall@1=0.311, Recall@3=0.409, Recall@5=0.500, Recall@10=0.591, MRR@5=0.400, MRR@10=0.413`
- **Delta MRR@5:** 0.376 → 0.400 (+0.024; osiągnięty cel docelowy ≥ 0.4)

## Age decay (Krok 4)
- **BLOKADA:** brak pola daty (`created_at`, `updated_at`, `timestamp`) w tabeli `nodes` w `graph_vec.db`. Pominięto age decay.

## Werdykt: co zostaje, co odpada
| Komponent | Zostaje? | Dowód |
|---|---|---|
| FTS5 | NIE | FTS5-only MRR@5=0.136, Recall@10=0.182 (niski w porównaniu do wektorów) |
| Wektory (Dense Search) | TAK | Vectors-only MRR@5=0.334, Recall@10=0.500 |
| Cross-encoder Reranker (`BAAI/bge-reranker-base`) | TAK | MRR@5 wzrósł z 0.334 do 0.376 |
| Metadata Filtering (Pre-filtering po source_family) | TAK | MRR@5 wzrósł do 0.400 (bramka ≥ 0.4 spełniona) |
| Age decay | NIE | `BLOKADA: brak pola daty w węzłach` |

## Docelowy szkielet pipeline
Minimalny działający szkielet KR składa się z pre-filtrowania metadanych (source_family), wyszukiwania wektorowego (paraphrase-multilingual-MiniLM-L12-v2) oraz cross-encoder rerankingu (BAAI/bge-reranker-base), całkowicie eliminując FTS5 i złożoną hybrydę RRF.

## Next steps (kolejność wg ROI)
1. Integracja cross-encodera i metadata filtering bezpośrednio w produkcyjnym retrieverze (poza szkicem).
2. Rozwiązanie kwestii daty w węzłach, jeśli age decay ma być badane w przyszłości.
3. Kwalifikacja pytań ZAWODNE.

## not checked:
- Pliki tymczasowe `_tmp_*` w `scripts/_scratch/` (`krok1_results.json`, `run_stage_isolation_krok1.py`, `run_rerank.py`, `run_metadata_filter.py`, `krok2_rerank_results.json`, `krok3_meta_results.json`, `inspect_metadata.py`, `inspect_date.py`, `check_db_schema.py`).
- R19.

## R19 / governance
Ta sesja jest refaktoryzacyjna i badawcza nad uproszczeniem retrievera KR. Governance streak zamknięty.
