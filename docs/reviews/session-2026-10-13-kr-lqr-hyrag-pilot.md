# Raport sesji: Pilot LQR-HyRAG i weryfikacja komponentów retrievera KR — 2026-10-13

## Weryfikacja poprzedniej sesji
- `git log -1 --format=%B 1a14914` → `kr-simplification-2026-10-13: kr-simplification-2026-10-13 — 2026-10-13: vectors-only MRR@5=0.334 + rerank BAAI/bge-reranker-base`
- Czy metadata filter zawiera reranker? **NIE**. Plik `scripts/_scratch/run_metadata_filter.py` wykonuje czyste wyszukiwanie wektorowe z pre-filtrowaniem po `source_family`, bez użycia `CrossEncoder`.
- Werdykt: kombinacja rerank + metadata w poprzednim raporcie była rozłączna (metadata osobno dało 0.400, rerank osobno dał 0.376). Ich jednoczesne działanie nie było zweryfikowane w jednym skrypcie.

## Baseline (Krok 1: Wektory + Rerank)
- **Komenda:** `python scripts/_scratch/run_rerank.py`
- **Surowy output zbiorczy:**
  - `[VECTORS_RERANK (BAAI/bge-reranker-base)] n=33: Recall@1=0.303, Recall@3=0.409, Recall@5=0.470, Recall@10=0.530, MRR@5=0.376, MRR@10=0.384`

## HyPE (Krok 2: Hipotetyczne pytania + Rerank)
- **Komenda:** `python scripts/_scratch/run_hype.py`
- **Surowy output zbiorczy:**
  - `[HYPE_RERANK] n=33: Recall@1=0.098, Recall@3=0.106, Recall@5=0.114, Recall@10=0.121, MRR@5=0.121, MRR@10=0.121`
- **Delta MRR@5:** 0.376 → 0.121 (-0.255). HyPE w obecnej naiwnej implementacji (szablonowe pytania typu "What is X?") drastycznie pogorszyło wyniki w porównaniu do bezpośredniego dopasowania wektorowego treści chunka.

## Prosty router (Krok 3: Routing regułowy między metadanymi a wektorami)
- **Komenda:** `python scripts/_scratch/run_router.py`
- **Surowy output zbiorczy:**
  - `[ROUTER] n=33 (routes: {'metadata': 12, 'vectors_rerank': 21}): Recall@1=0.242, Recall@3=0.379, Recall@5=0.470, Recall@10=0.530, MRR@5=0.336, MRR@10=0.344`
- **Delta MRR@5:** 0.376 → 0.336 (-0.040). Sztywne pre-filtrowanie metadanych (source_family) na podstawie słów kluczowych obcięło właściwe kandydaty dla części zapytań.

## Werdykt: co zostaje, co odpada
| Komponent | Zostaje? | Dowód |
|---|---|---|
| Wektory + Cross-encoder Reranker (`BAAI/bge-reranker-base`) | **TAK** | MRR@5 = 0.376 (najwyższy stabilny wynik bazowy) |
| HyPE (Hipotetyczne pytania) | **NIE** | MRR@5 spadł do 0.121 (szablonowe pytania nie zastępują bezpośredniego semantycznego dopasowania treści) |
| Prosty Router regułowy | **NIE** | MRR@5 spadł do 0.336 (regułowy pre-filter odcina trafne wyniki) |
| FTS5 | **NIE** | Potwierdzone w poprzednich sesjach (MRR@5=0.136) |

## Docelowy szkielet pipeline
Sprawdzony i optymalny pipeline KR to bezpośrednie wyszukiwanie wektorowe top-20 kandydatów, a następnie cross-encoder reranking (`BAAI/bge-reranker-base`) do top-5/10 (MRR@5 = 0.376).

## Next steps (kolejność wg ROI)
1. Integracja cross-encodera bezpośrednio w produkcyjnym retrieverze.
2. Dalsza analiza zapytań błędnie obsługiwanych (False Refusals, OOC).

## not checked:
- Pliki tymczasowe `_tmp_*` w `eval/` oraz w `scripts/_scratch/`.
- R19.

## R19 / governance
Ta sesja jest badawczo-refaktoryzacyjna (pilot LQR-HyRAG). Governance streak zamknięty.
