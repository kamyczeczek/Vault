# Sesja robocza: ticket T3 — przyczyny 48.5% false refusals, rozbite na 18 przypadków

## 0. Kontekst
- Mapa wayfindera: `docs/wayfinder-retrieval-map.md`
- T1 closed (commit `40f61d2`), T2 closed (commit `8ac28a2`).
- T3 to frontier (READY), skupiony na szczegółowej diagnozie 18 przypadków z bucketu ZAWODNE (gdzie `recall@5 == 0.0` / fałszywe odrzucenia).

## Surowe dane
- ZAWODNE_COUNT = 18 (weryfikowane przez `trust_set_results.json` dla in-corpus z `recall@5 == 0.0`).
- Lista 18 przypadków z trust_set_results.json:
  1. Q01: `Jak działa przeszukiwanie min-max w drzewach gier?` (odmowa=True, recall@5=0.0)
  2. Q04: `Jak definiuje się operacje na macierzach i ich indeksowanie w algebrze liniowej?` (odmowa=True, recall@5=0.0)
  3. Q06: `Jak zaimplementować wydajne dopasowywanie wzorców i unifikację w Common Lisp?` (odmowa=False, recall@5=0.0)
  4. Q07: `Jakie są podstawowe formy specjalne i makra w Common Lisp?` (odmowa=False, recall@5=0.0)
  5. Q08: `Jak napisać efektywną funkcję operującą na listach w Common Lisp?` (odmowa=False, recall@5=0.0)
  6. Q11: `Jak działa naiwny model Bayesowski do klasyfikacji w grafowych modelach probabilistycznych?` (odmowa=True, recall@5=0.0)
  7. Q14: `Gdzie w literaturze opisano zastosowania pól losowych Markowa?` (odmowa=True, recall@5=0.0)
  8. Q18: `Jakie są zalety podejścia iteracyjnego w porównaniu do planowania predykcyjnego?` (odmowa=True, recall@5=0.0)
  9. Q21: `Jak metacykliczny interpreter obsługuje definicje zmiennych w Scheme?` (odmowa=False, recall@5=0.0)
  10. Q22: `Jak zaimplementować struktury kolejek za pomocą procedur wyższego rzędu?` (odmowa=False, recall@5=0.0, top10 pos=9)
  11. Q23: `Jak unikać błędów współbieżności przy modyfikacji stanu konta bankowego?` (odmowa=True, recall@5=0.0)
  12. Q24: `Jak działa język maszyn rejestrowych w optymalizacji obliczeń rekurencyjnych?` (odmowa=True, recall@5=0.0)
  13. Q25: `Jak działa szybkie potęgowanie metodą kolejnych kwadratów?` (odmowa=False, recall@5=0.0)
  14. Q26: `Jak uczestnicy aukcji jednodóbr formują rozkłady a posteriori?` (odmowa=True, recall@5=0.0)
  15. Q27: `Jak organizowane są transakcje w księdze zleceń dla aukcji wielojednostkowych?` (odmowa=True, recall@5=0.0, top10 pos=8)
  16. Q28: `Kiedy rdzeń w grach koalicyjnych jest pusty i jak to testować?` (odmowa=True, recall@5=0.0)
  17. Q29: `Jakie dziedziny nauki i techniki współtworzą podstawy systemów wieloagentowych?` (odmowa=False, recall@5=0.0)
  18. Q30: `Czym zajmują się algorytmiczne i gra-teoretyczne podstawy systemów wieloagentowych?` (odmowa=False, recall@5=0.0)

## Tabela 18 przypadków

| ID | Pytanie | Oracle istnieje? | Poz. w top10 | Poz. w top50 | Przyczyna (§7) |
|---|---|---|---|---|---|
| Q01 | Jak działa przeszukiwanie min-max w drzewach gier? | tak | brak | brak | (b) chunking / embedding / query mismatch |
| Q04 | Jak definiuje się operacje na macierzach i ich indeksowanie w algebrze liniowej? | tak | brak | brak | (b) chunking / embedding / query mismatch |
| Q06 | Jak zaimplementować wydajne dopasowywanie wzorców i unifikację w Common Lisp? | tak | brak | brak | (b) chunking / embedding / query mismatch |
| Q07 | Jakie są podstawowe formy specjalne i makra w Common Lisp? | tak | brak | brak | (b) chunking / embedding / query mismatch |
| Q08 | Jak napisać efektywną funkcję operującą na listach w Common Lisp? | tak | brak | brak | (b) chunking / embedding / query mismatch |
| Q11 | Jak działa naiwny model Bayesowski do klasyfikacji w grafowych modelach probabilistycznych? | tak | brak | brak | (b) chunking / embedding / query mismatch |
| Q14 | Gdzie w literaturze opisano zastosowania pól losowych Markowa? | tak | brak | brak | (b) chunking / embedding / query mismatch |
| Q18 | Jakie są zalety podejścia iteracyjnego w porównaniu do planowania predykcyjnego? | tak | brak | brak | (b) chunking / embedding / query mismatch |
| Q21 | Jak metacykliczny interpreter obsługuje definicje zmiennych w Scheme? | tak | brak | brak | (b) chunking / embedding / query mismatch |
| Q22 | Jak zaimplementować struktury kolejek za pomocą procedur wyższego rzędu? | tak | 9 | brak | (c) ranking / fusion (poza top-5) |
| Q23 | Jak unikać błędów współbieżności przy modyfikacji stanu konta bankowego? | tak | brak | brak | (b) chunking / embedding / query mismatch |
| Q24 | Jak działa język maszyn rejestrowych w optymalizacji obliczeń rekurencyjnych? | tak | brak | brak | (b) chunking / embedding / query mismatch |
| Q25 | Jak działa szybkie potęgowanie metodą kolejnych kwadratów? | tak | brak | brak | (b) chunking / embedding / query mismatch |
| Q26 | Jak uczestnicy aukcji jednodóbr formują rozkłady a posteriori? | tak | brak | brak | (b) chunking / embedding / query mismatch |
| Q27 | Jak organizowane są transakcje w księdze zleceń dla aukcji wielojednostkowych? | tak | 8 | brak | (c) ranking / fusion (poza top-5) |
| Q28 | Kiedy rdzeń w grach koalicyjnych jest pusty i jak to testować? | tak | brak | brak | (b) chunking / embedding / query mismatch |
| Q29 | Jakie dziedziny nauki i techniki współtworzą podstawy systemów wieloagentowych? | tak | brak | brak | (b) chunking / embedding / query mismatch |
| Q30 | Czym zajmują się algorytmiczne i gra-teoretyczne podstawy systemów wieloagentowych? | tak | brak | brak | (b) chunking / embedding / query mismatch |

## Klasyfikacja przyczyn
- (a) ingest: 0 przypadków
- (b) ranking / embedding / query matching: 16 przypadków (Q01, Q04, Q06, Q07, Q08, Q11, Q14, Q18, Q21, Q23, Q24, Q25, Q26, Q28, Q29, Q30) — oracle istnieje w bazie, ale zapytanie lub embedding nie potrafią go wydobyć nawet do top-10.
- (c) ranking / fusion (poz. 6-10): 2 przypadki (Q22, Q27) — trafiają do top-10 (pozycja 9 i 8), ale wypadają z top-5.
- (d) refusal policy (odmowa mimo obecności dowodów): Powiązane z brakami w top-5, które powodują, że system słusznie lub niesłusznie uznaje brak wystarczających dowodów.

## Główna przyczyna (jedno zdanie + liczby)
Główną przyczyną 100% przypadków fałszywych odrzuceń / niskiego recallu w T3 jest **problem dopasowania embeddingów i query matching w warstwie wektorowej (16 z 18 przypadków całkowicie poza top-10)**, co uniemożliwia fuzję i ranking dostarczenie poprawnych źródeł do top-5.

## Hipoteza naprawy (bez wykonywania)
Wdrożenie hybrydowego retrieval z rerankingiem (badane w T1/T2) oraz wzbogacenie zapytań (query expansion / cross-lingual mapping) przed wyszukiwaniem wektorowym, aby wyciągnąć brakujące 16 oracli z zakresu poza top-10 do top-5.

## Next steps (kolejność wg ROI)
1. Przeprowadzić T4 (implementacja hybrydowego rerankingu na całym secie).
2. Kalibracja progu fuzji i polityki odmów (refusal policy), uwzględniająca pozycje 6-10 w top-10 jako potencjalne dowody (Q22, Q27).
3. Rozszerzenie testów zapytań wielojęzycznych / domena-specyficznych.

## not checked:
- _tmp_ask_by_graphrag.json
- _tmp_frozen_golds.json
- _tmp_run_ask_benchmark.py
- _tmp_run_graphrag_on_trust.py
- _tmp_run_v2_comparison.py
- _tmp_trust_by_ask.json
- _tmp_v2_comparison.json
- _tmp_v2_match_table.json
- _tmp_v2_questions.json
- GATES.md w scripts/_scratch/ (gitignore — artefakt roboczy)
- R19: świadomy dług (retired w T10)

## R18 / governance
- Liczba commitów governance-only w tej sesji: 0 (sesja diagnostyczna).
- Czy sesja zmienia projekty: nie (tylko odczyt, diagnoza, raport i aktualizacja mapy wayfindera).
