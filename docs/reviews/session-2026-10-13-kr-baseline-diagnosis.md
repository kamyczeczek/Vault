# Raport sesji: Baseline i Diagnoza Retrievera KR — 2026-10-13

## Baseline (Krok 1)
- **Tool call:** `python projects/research/knowledge-retrieval/pilots/graphrag/eval/measure_trust_set.py`
- **Surowy output (podsumowanie z eval harness):**
  - IN-CORPUS (n=33): Recall@1=0.159, Recall@3=0.417, Recall@10=0.515, MRR=0.303, MRR@5=0.295, Recall@5=0.455
  - OUT-OF-CORPUS refusal (n=15): 100.0% (15/15)
  - BOUNDARY refusal (n=10): 50.0% (5/10)
  - FALSE REFUSAL in-corpus (n=33): 48.5% (16/33)

## Diagnoza per etap (Krok 2)
### 1. Retrieval (Recall@K)
- **Wynik:** Recall@1 = 0.159, Recall@3 = 0.417, Recall@5 = 0.455, Recall@10 = 0.515.
- **Interpretacja:** Ponad połowa relevantnych dokumentów (oracles) w ogóle nie trafia do top-10 dla naturalnych pytań (szczególnie w bucketach ZAWODNE: algorytmy, Lisp, PRML, SICP, multiagent systems), co wskazuje na ograniczenia FTS5 / dopasowania słów kluczowych przy pytaniach naturalnych sformułowanych po polsku/angielsku bez dosłownych tokenów z ID dokumentów.

### 2. Ranking (MRR/NDCG)
- **Wynik:** MRR@5 = 0.295, MRR = 0.303.
- **Interpretacja:** Gdy oracle trafia do top-10, rzadko jest na pozycji 1 (Recall@1 jest niski). Jednak Recall@5 (0.455) i Recall@10 (0.515) pokazują, że głównym problemem nie jest całkowity brak dokumentu w bazie, lecz jego niska pozycja (ranking) lub brak w top-5.

### 3. Attribution (False Refusals)
- **Wynik:** 48.5% false refusal in-corpus (16/33 pytań odrzuconych mimo obecności w korpusie).
- **Interpretacja:** Rygorystyczny mechanizm `MIN_KEYWORD_MATCHES=2` w połączeniu z automatyczną ekstrakcją słów kluczowych z naturalnych pytań powoduje masowe odrzucenia (odmowy), ponieważ sformułowania użytkownika różnią się od wewnętrznego słownika węzła.

## Hipoteza
Głównym wąskim gardłem retrievera KR dla naturalnych pytań jest **dwupoziomowa rozbieżność**: (1) w warstwie retrievalu/rankingu FTS5 słabo radzi sobie z mapowaniem naturalnych zapytań na unikalne ID/tytuły dokumentów (skutkując niskim Recall@5 = 0.455 i MRR@5 = 0.295), a (2) w warstwie attribution/synthesis zbyt restrykcyjna polityka dopasowania słów kluczowych (`MIN_KEYWORD_MATCHES=2`) wywołuje 48.5% false refusals.

## Eksperyment potwierdzający (Krok 3)
- **Status:** Nie wykonano edycji kodu. Zgodnie z zasadami sesji badawczej, żadne parametry ani kod nie zostały zmodyfikowane.

## Next steps (kolejność wg ROI)
1. **Kalibracja ekstrakcji słów kluczowych i progu attribution:** złagodzenie lub uelastycznienie `MIN_KEYWORD_MATCHES` w `oblicz_pokrycie()` w celu obniżenia 48.5% false refusals.
2. **Poprawa rankingu FTS5 / hybrydy:** wzbogacenie zapytań o synonimy lub kalibracja wag embeddingów wektorowych (`prog_cosine` / hybryda ON/OFF), aby podnieść Recall@5 powyżej progu 0.45.
3. **Analiza bucketu ZAWODNE:** szczegółowy przegląd 18 pytań niespełniających top-5 w celu zidentyfikowania brakujących aliasów w węzłach korpusu.

## not checked:
- Ręczna kwalifikacja 18 pytań ZAWODNE pod kątem poprawności goldów.
- Wpływ włączenia/wyłączenia semantycznego na pełnym zbiorze 58 pytań z nowymi wagami.

## R18 / governance
Ta sesja jest badawcza. Governance streak zamknięty w `workflow-verification-fix-2026-10-13`. Nie otwarto nowej warstwy governance.
