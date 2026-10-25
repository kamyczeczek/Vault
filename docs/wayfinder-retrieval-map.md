# Wayfinder Map: Doprowadzenie do sprawnego retrieval (3 domeny)

## Destination

Każda z 3 domen (książki, historia sesji, stan workspace) ma zmierzony baseline, zdiagnozowane błędy, test przekrojowy i czasowy; każda liczba ma artefakt.
Uwaga (sesja 17/10): paradoks 0.938 vs 0.295 rozstrzygnięty jako C (różne metryki, obie liczby poprawne).

## Notes

- **Domeny:** Książki (Knowledge Retrieval), Historia sesji (`memory_index.py` / sesje opencode/cline), Stan workspace (`WORKSPACE_ROOT`, `WORKSPACE_STATE`).
- **Skille do konsultacji:** `wayfinder`, `unlazy`, `icm-architect`, `improve-codebase-architecture`.
- **Preferencje:** Każda liczba w raporcie musi mieć artefakt z tool calla; zero restate'owania dokumentów jako faktów; zero `env`/`printenv`.

## Decisions so far

- [T3](docs/reviews/session-2026-10-13-kr-t3-false-refusals.md): 18 false refusals rozbite na 18 przypadków, główna przyczyna = problem dopasowania embeddingów i query matching (16/18 przypadków poza top-10).
- [T3-verify](docs/reviews/session-2026-10-13-kr-t3-verification.md): oracles istnieją w graph_vec.db (18/18); rozbieżność wyjaśniona — pusta graph.db (0 bajtów); defect class 4 potwierdzony (family match, nie embedding mismatch).
- [T13](docs/reviews/session-2026-10-13-kr-t13-gold-id-verification.md): 16/18 ZAWODNE to family-match-only (88.9%); metryka recall@5 mierzy annotację, nie retrieval — retired w measurements.md.
- [T2](docs/reviews/session-2026-10-13-kr-t2-measure-script.md): measure_trust_set.py mierzy hybrydę — linia 34 (`plan.uzyj_wektorow = True`).
- [T1](docs/reviews/session-2026-10-13-kr-t1-rerank-baseline.md): vectors+rerank MRR@5=0.376 na Trust Secie (odtworzone z historycznym 0.376).
- [Workflow-enforcement]: cztery mechanizmy (scan_secrets, pre_close_check, verify_report_evidence, close.py body fix). Mapowanie SCARS→mechanizm w docs/workflow/README.md.
- [Workflow-debt-closure]: R19 działała poprawnie (fire na untracked oryginale, nie na retired-fladze) — długiem był sam plik, usunięty za zgodą właściciela, bez zmian w bramce (S62). R16 to advisory z oknem 30 min, drzwi debug-with-memory nie miały zastosowania (decyzja w docs/workflow/README.md). verify_report_evidence ma --enforce-after (cutoff 2026-10-14) i jest wpięte w pre_close_check krok 11. docs/workflow/ ma kontrakt (CONTEXT.md) + routing z root CLAUDE.md. T10 tym rozstrzygnięte (wiersz T10 nietknięty per zakres sesji).
- [Chain-non-convergence-2026-10-14]: 11 sesji, 2 otwarte tematy, zero konwergencji. T18: warianty MIN_KEYWORD 1/2/3 zmierzone — 0 flips odmowy/58 pytań, gałka martwa. Łańcuch zamknięty jako finding. Dalsze sesje wymagają decyzji właściciela.
- [KR-pilot-terminated-2026-10-14]: pilot GraphRAG zamknięty jako terminated, gate not met. MRR@5=0.295 < 0.4 (gate oblany 4. raz). Semantic OFF→ON: false refusals 27.3%→0.0%, OOC refusal 66.7%→40.0% (4x OOC O02/O06/O10/O14 złamane), BOUNDARY 0.0% w obu. Brak punktu akceptowalnego (regresja OOC 26.7pp > limit 10pp; strojenie prog_cosine poza zakresem, S62). Mur #2 (q_emb=None) naprawiony i zmierzony jako przyczyna, nie fix.
- [Chain-closed-2026-10-14]: łańcuch 12 sesji zamknięty. L1-contracts accepted-debt (507 KB), KR pilot terminated-final, łańcuch closed. Dalsze sesje w tych tematach zabronione bez nowej decyzji właściciela.
- [KR-closed-2026-10-14]: KR dopięty. Kod KR repo: semantic OFF (jak zawsze). Dokumentacja (`measurements.md`): jawnie opisuje kontekst pomiaru semantic ON vs OFF. Otwarte tickety KR zamknięte jako not-reached. Dalsze sesje KR wymagają nowej decyzji właściciela.
- [T7-kr-benchmark-scope](docs/reviews/session-2026-10-14-kr-benchmark-scope.md): benchmark KR mierzy ranking hybrydowy (wektory ON, semantic OFF) na 33 pytaniach in-corpus plus odmowy na 15 OOC i 10 boundary; recall@5 retired, family_recall@5 bez agregatu, raport z 2026-10-11 zamrożony względem kodu.
- [Retrieval-paradox-2026-10-14](docs/reviews/session-2026-10-14-retrieval-paradox.md): C (różne metryki). mean_family_recall=0.938 mierzy trafienie w slug na 8 przypadkach EN, MRR@5=0.295 mierzy exact chunk-ID z rangą na 33 pytaniach in-corpus; family_recall@5 na Trust Secie = 0.939 (równe 0.938), więc luka jest między metrykami, nie zbiorami. Sprawny retrieval? NIE WIEM — zależy od wyboru bramki przez właściciela.
- [Local-rag-map-started]: nowa mapa `docs/wayfinder-local-rag-map.md` dla osobistego lokalnego RAG na bibliotece książek. KR (`terminated`) zamknięty; ta mapa to nowy effort, nie kontynuacja.
- [Local-rag-map-extended]: mapa `docs/wayfinder-local-rag-map.md` rozszerzona o PageIndex i porównanie metod. 15 ticketów (R1-R15), 12 bramek (G0-G12).

## Not yet specified

- Szczegółowe formaty danych i schematy rekordów dla historii sesji i stanu workspace.
- Dokładny kształt automatycznego harnessu do testów czasu i sprzeczności między domenami.
- Identyfikacja wszystkich cichych krawędzi (edge cases) przy próbach scalenia hybrydowego indeksu z lokalnymi pamięciami sesyjnymi.

## Out of scope

- Trenowanie nowych modeli LQR.
- Wprowadzanie nowych embeddingów lub zewnętrznych wektorów bez uprzedniej diagnozy.
- Przepisywanie całej architektury retrieval bez dowodu empirycznego (delta przed/po).

---

## Tickets (Child Issues)

| ID | Typ | Tytuł | Status | Blokowane przez |
|---|---|---|---|---|
| T1 | research | Czy vectors+rerank nadal daje MRR@5 = 0.376 na Trust Secie? | closed | — |
| T2 | research | Co dokładnie mierzy `measure_trust_set.py` — hybrydę czy vectors+rerank? | closed | — |
| T3 | research | Jakie są konkretne przyczyny 48.5% false refusals? Rozbij na 18 przypadków. | closed | T1, T2 (T3: closed) |
| T4 | research | Czy `memory_index.py` (hit@5=1.0) nadal działa i na jakim zbiorze? | closed (sesja 11) | — |
| T5 | task | Zidentyfikuj wszystkie źródła danych dla 3 domen (książki, historia sesji, stan workspace). | closed-not-reached (łańcuch zamknięty sesją 12/10) | — |
| T6 | prototype | Naszkicuj wspólny interfejs retrieval (sygnatura funkcji, wejście/wyjście) dla 3 domen. | closed-not-reached (łańcuch zamknięty sesją 12/10) | T5 |
| T7 | research | Co mierzy benchmark KR obecnie? Przeczytaj `references/defect-classes.md`, `measurements.md`. | closed (sesja 15) | — |
| T8 | task | Zebierz 10–20 pytań testowych per domena + 5 przekrojowych. | closed-not-reached (łańcuch zamknięty sesją 12/10; test set istnieje: 58 pytań) | T6 |
| T9 | research | Jak obsłużyć czas i sprzeczności? Przeczytaj istniejące podejścia w KR. | closed-not-reached (łańcuch zamknięty sesją 12/10) | — |
| T10 | task | Rozstrzygnij R19 — retired flagi nie wyciszył bramki w `check_workspace_integrity.py`. | closed | — |
| T11 | task | Sprawdź `knowledge_retrieval.txt` pod kątem kluczy API przy użyciu grep. | closed (sesja 16): plik nie istnieje | — |
| T12 | research | Zdiagnozuj MAP.md is stale — co konkretnie było nieaktualne? | closed-not-reached (łańcuch zamknięty sesją 12/10) | — |
| T13 | research | Weryfikacja gold IDs w Trust Secie względem aktualnego re-ingestu — czy retrieval zwraca exact gold, czy inny chunk tego samego sluga? | closed | — |
| T14 | task | Automatyczny triage instrukcji > 3 cele → STOP i mapa ticketów | closed-not-reached (łańcuch zamknięty sesją 12/10) | — |
| T15 | task | Auto-fix stale views (HANDOFF.md, MAP.md) przy pierwszym advisory | closed-not-reached (łańcuch zamknięty sesją 12/10; build_handoff już się tym zajmuje) | — |
| T16 | task | Weryfikator bramek przepisanych po niepowodzeniu (S62) | closed-not-reached (łańcuch zamknięty sesją 12/10) | — |
| T17 | task | R16 fires dla zmian w scripts/** bez nieznanego błędu (fałszywy pozytyw). Rozstrzygnij: skip dla nowych plików LUB dla zmian w plikach `scripts/scan_secrets.py`, `scripts/pre_close_check.py`, `scripts/verify_report_evidence.py` | closed-not-reached (łańcuch zamknięty sesją 12/10) | — |
| T-L1-contracts-size | task | L1-contracts 507,428 B > 250 KB. accepted-debt (sesja 12): cięcie wymaga decyzji właściciela o architekturze handoffu. Główny składnik: HANDOFF.md 187,359 B. | closed-accepted-debt | — |
| T-retrieval-v2-corpus | task | retrieval-v2/corpus/ (10k+ derived .md z export_corpus.py) wchodzi do L1-full. Exclude w projects.json. | closed (sesja 5) | — |
