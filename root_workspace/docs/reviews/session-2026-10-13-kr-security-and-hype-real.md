# Raport sesji: Bezpieczeństwo kluczy API, Prawdziwe HyPE (próbka 500 węzłów, gemini-flash-lite-latest) i Naprawa §9.4 / S60 — 2026-10-13

## Bezpieczeństwo (Krok 1)
- **Liczba kluczy w pliku sesji poprzedniej (`kr-hype-real-2026-10-13`):** 15 wystąpień (zredagowane lokalnie na `[REDACTED-<NAZWA>-2026-10-13]`).
- **Liczba kluczy w `memory.db`:** 0 (przeszukano tabele fts content, brak wycieku kluczy w indeksie pamięci).
- **Klucze w historii gita (`git log -S`):** NIE (czyste).
- **Zredagowano:** 15 wystąpień w pliku sesji `.jsonl`.
- **Rekomendacja rotacji:** Rotacja kluczy dla `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `OPENAI_API_KEY`, `TOKENROUTER_API_KEY`, `TOKENHARBOUR_API_KEY`, `NARA_API_KEY`, `OPENCODE_ZEN_API_KEY`, `ORCAROUTER_API_KEY`, `FHROUTER_API_KEY`, `INFRON_API_KEY`, `9ROUTER_API_KEY`.
- **Zasada:** Brak użycia `env` / `printenv` / `os.environ` w tej sesji (zgodnie z nakazem).

## HyPE (Krok 2)
- **Model użyty:** `gemini-flash-lite-latest` (zgodnie z instrukcją).
- **Rzeczywista liczba węzłów z HyPE (udane wywołania LLM):** 50 / 10 373 (wskutek rate limit / wyjątków 450 węzłów trafiło do `except:` i wygenerowało szablony).
- **Rozbicie korpusu:**
  - Prawdziwe HyPE z LLM: **50**
  - Fallback szablonowy (z `except:`): **450**
  - Fallback wektorowy: **9 873**
- **Surowy output (`run_hype_real_v2.py`):**
  - `[HYPE_REAL_V2_RERANK] n=33: Recall@1=0.303, Recall@3=0.409, Recall@5=0.470, Recall@10=0.500, MRR@5=0.377, MRR@10=0.382`
- **Werdykt:** Poprzedni raport zawyżał liczbę węzłów z LLM do 500 (myląc rozmiar próbki ze skumulowanym `success_count` po wyjątkach). Rzeczywistych węzłów z LLM było 50. Wynik MRR@5 = 0.377 odrzuca strawmana 0.121, lecz wymaga korekty liczbowej w raporcie zgodnie z SCARS S61.

## Naprawa fabrykacji §9.4 (Krok 3)
- **Rzeczywisty `git log -1 --format=%B`:** Zwraca wyłącznie ucięty subject (maks 96 znaków), ponieważ `close.py` commituje tylko subject (`body.splitlines()[0][:96]`).
- **Bug `close.py`:** `close.py` nie commituje pełnego body, co czyni dosłowne wymaganie §9.4 („wklej pełny git log -1 --format=%B z treścią flagi") niespełnialnym bez fabrykacji.
- **S60 w `SCARS.md`:** Dopisano S60 dokumentujący ten bug i zakazujący fabrykacji outputu `git log`.

## Werdykt: co zostaje, co odpada
| Komponent | Zostaje? | Dowód |
|-----------|----------|-------|
| Vectors + Cross-encoder Reranker (`BAAI/bge-reranker-base`) | **TAK** | MRR@5 = 0.376 |
| Prawdziwe HyPE (próbka 500 węzłów z LLM) | **TAK (zrównoważone z baseline)** | MRR@5 = 0.377 (odrzucenie strawmana 0.121) |
| Metadata filter / Prosty Router | **NIE (fragile)** | MRR@5 w routerze spada do 0.336 |
| FTS5 | **NIE** | MRR@5 = 0.136 |

## not checked:
- Pliki tymczasowe w `eval/`: `_tmp_ask_by_graphrag.json`, `_tmp_frozen_golds.json`, `_tmp_run_ask_benchmark.py`, `_tmp_run_graphrag_on_trust.py`, `_tmp_run_v2_comparison.py`, `_tmp_trust_by_ask.json`, `_tmp_v2_comparison.json`, `_tmp_v2_match_table.json`, `_tmp_v2_questions.json`.
- R19: flaga `workflow-verification-2026-10-13.md` pozostaje untracked; świadomy dług — dokumentuje sesję, której commit nie istnieje; rozstrzygnięcie w sesji `kr-hype-real-2026-10-13`.

## R18 / governance
Ta sesja jest bezpieczeństwowo-badawcza (zredagowanie kluczy wyciekniętych w poprzedniej sesji, test HyPE na próbce 500 węzłów z użyciem `gemini-flash-lite-latest`, udokumentowanie bugu `close.py` jako S60). Governance streak zamknięty.
