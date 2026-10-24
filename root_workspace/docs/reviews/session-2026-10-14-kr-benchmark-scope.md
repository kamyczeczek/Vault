# KR benchmark — co mierzy obecnie (2026-10-14)

<!-- audit:begin -->
## Kontekst
Sesja 15/10: ticket T7. Diagnostic scope — co benchmark KR faktycznie mierzy,
na jakim zbiorze, w jakim trybie, i co dokumentacja mówi inaczej niż kod.

## Test set
Test set to `pilots/graphrag/eval/questions.md`: 58 pytań, w tym 33 in-corpus
(3 bazowe Q00a-c plus 30 naturalnych Q01-Q30), 15 out-of-corpus (O01-O15,
oczekiwana odmowa) oraz 10 boundary (B01-B10, bliska domena, oczekiwana odmowa).
In-corpus ma przypisane oracle ID (exact chunk ID), OOC i boundary mają myślnik.

## Co mierzy `measure_trust_set.py` (verbatim z kodu)
Skrypt mierzy retrieval na pełnym teście (in-corpus plus OOC plus boundary),
read-only; wynik to stdout plus `trust_set_results.json`. Kluczowe linie:

```
K = 10
plan.uzyj_wektorow = True  # hybryda ON
pokryte = g.oblicz_pokrycie(wyniki, plan.slowa_kluczowe)  # semantic OFF
wynik = g.syntezuj_odpowiedz(q["pytanie"], pokryte)
```

Czyli: retrieval hybrydowy (wektory ON), pokrycie liczone keyword-only
(`pytanie=` nie jest przekazane do `oblicz_pokrycie` — idzie tylko
`plan.slowa_kluczowe`), a odmowa pochodzi z syntezy na pokrytych chunkach.
Per pytanie in-corpus z oracles liczone są: recall@1, recall@3, recall@10,
recall@5, mrr, mrr@5, ndcg@5 oraz family_recall@5. Agregaty na stdout to średnie
in-corpus (Recall@1, Recall@3, Recall@10, MRR, MRR@5, Recall@5) oraz trzy stopy
odmów: OOC refusal, BOUNDARY refusal, FALSE REFUSAL in-corpus. Uwaga:
family_recall@5 jest liczone per wiersz, ale nie ma agregatu na stdout.

Bieżący pomiar z tej sesji (kod po zmianach z 2026-10-13):

```
IN-CORPUS (n=33): Recall@1=0.159 Recall@3=0.417 Recall@10=0.515 MRR=0.303 MRR@5=0.295 Recall@5=0.455
OOC refusal (n=15): 66.7%
BOUNDARY refusal (n=10): 0.0%
FALSE REFUSAL in-corpus (n=33): 27.3%
```

Historyczny `trust_set_report.md` z 2026-10-11 (semantic gate OFF, próg 0.45)
raportował identyczny ranking: MRR@5 0.295 i Recall@5 0.455, ale inne odmowy:
OOC refusal 100.0% (15/15), BOUNDARY refusal 50.0% (5/10) oraz FALSE REFUSAL
48.5% (16/33). Ranking stoi w miejscu, zachowanie odmów zmieniło się wraz
ze zmianą kodu (poprawa z 0.207 do 0.295 MRR@5 i z 0.242 do 0.455 Recall@5
względem jeszcze wcześniejszego zestawu szablonowego pochodzi z tamtego raportu).

## Metryki: co jest mierzone, co jest retired
Dwie warstwy. Warstwa Trust Set (58 pytań, skrypt powyżej): mierzone
recall@1, recall@3, recall@5, recall@10, mrr, mrr@5, ndcg@5, family_recall@5
(per wiersz), OOC refusal, BOUNDARY refusal, false refusal. Retired w tej
warstwie: recall@5 na Trust Secie (retired 2026-10-13 — mierzy adnotację
exact ID, nie retriever; dowód: w 16 z 18 rzekomych false refusals, czyli
88.9%, retriever zwraca poprawny chunk tego samego sluga, family recall 88.9%
przy exact recall 0%; zastąpienie: family_recall@5).

Warstwa `references/measurements.md` (8 przypadków benchmarkowych, inne źródło
prawdy): mean_family_recall 0.938 (wzrost z 0.875, czyli 93.8% across families),
concept_coverage 1.000 (100% across 8 cases), mean_family_precision 0.654
(wzrost z 0.629), mean_exact_recall 0.312 (wzrost z 0.250), latency 99.4 ms,
corpus damage 4.0% (419/10364), glued tokens 3 (było 1784). Retired tutaj:
mean_exact_recall 0.25 (trzy dowody: gold bez termu zapytania, gold na pozycji
11/386, 18/191, 76/210 przy darmowej rodzinie, 6 z 8 goldów to front matter).
Superseded: 62% corpus-damage (detektor over-firing: 6401 zgłoszeń zamiast
prawdziwych 419) oraz kwarantanna na poziomie źródła (poświęcała 417 czystych
chunków dla 419 uszkodzonych, w tym całe 828 chunków Paradigms i 1123 AIMA).
Not yet measured: ranking wewnątrz poprawnej rodziny (precision 0.746),
latency p95 pod bramką tokenową, pytania wielohopowe (one-hop daje plus 0.0323
recall, two-hop nigdy nie uruchomiony).

## Rozbieżności dokumentacja-vs-kod
1. `measurements.md` opisuje warstwę 8 przypadków, a skrypt mierzy 58 pytań —
   brak linku między warstwami, czytelnik nie wie, która liczba skąd pochodzi.
2. recall@5 jest retired od 2026-10-13, ale skrypt nadal drukuje Recall@5 0.455
   jako nagłówkowy agregat, a family_recall@5 (zalecany zamiennik) nie ma
   agregatu — nagłówek promuje martwą metrykę.
3. `measurements.md` wewnętrznie niespójny: tabela mówi mean_family_precision
   0.654, sekcja Not yet measured mówi 0.746, a `defect-classes.md` mówi
   0.652 strzałka 0.746 (przy 428 uszkodzonych chunkach strzałka 2).
4. Raport z 2026-10-11 vs bieżący pomiar: ten sam ranking (MRR@5 0.295,
   Recall@5 0.455), rozjechane odmowy (OOC 100.0% strzałka 66.7%, BOUNDARY
   50.0% strzałka 0.0%, FALSE 48.5% strzałka 27.3%) — raport zamrożony,
   kod poszedł dalej bez nowego raportu.

## Wniosek
Benchmark KR mierzy obecnie ranking hybrydowy (wektory ON, semantic OFF) na
33 pytaniach in-corpus oraz stopy odmów na 15 pytaniach OOC i 10 boundary,
a nie mierzy już niczego exact-ID (retired) ani rankingu wewnątrz rodziny.

## Tool calls
| Wartość | Komenda | Surowy output (fragment) |
|---|---|---|
| 0.938 | `cat references/measurements.md` | `mean_family_recall 0.938` |
| 0.875 | `cat references/measurements.md` | `up from 0.875 baseline` |
| 93.8% | `cat references/measurements.md` | `93.8% across all benchmark families` |
| 1.000 | `cat references/measurements.md` | `concept_coverage 1.000` |
| 100% | `cat references/measurements.md` | `100% required concept coverage` |
| 0.654 | `cat references/measurements.md` | `mean_family_precision 0.654` |
| 0.629 | `cat references/measurements.md` | `up from 0.629 baseline` |
| 0.312 | `cat references/measurements.md` | `mean_exact_recall 0.312` |
| 0.250 | `cat references/measurements.md` | `up from 0.250` |
| 99.4 | `cat references/measurements.md` | `mean latency 99.4 ms` |
| 4.0% | `cat references/measurements.md` | `corpus damage 4.0%` |
| 419/10364 | `cat references/measurements.md` | `corpus damage 419/10364` |
| 62% | `cat references/measurements.md` | `was reported as 62%` |
| 1784 | `cat references/defect-classes.md` | `1,784 glue tokens, glued tokens 1784` |
| 0.25 | `cat references/measurements.md` | `Retired: mean_exact_recall (0.25)` |
| 0.746 | `cat references/measurements.md` | `family precision is 0.746` |
| 0.652 | `cat references/defect-classes.md` | `mean_family_precision 0.652` |
| 0.0323 | `cat references/measurements.md` | `Experiment C, +0.0323 recall` |
| 0.45 | `cat pilots/graphrag/eval/trust_set_report.md` | `calibrated threshold 0.45` |
| 6401 | `cat references/defect-classes.md` | `It reported 6,401 defects, true count 419` |
| 419 | `cat references/defect-classes.md` | `the true count was 419` |
| 428 | `cat references/defect-classes.md` | `428 damaged chunks` |
| 0.159 | `python measure_trust_set.py` | `Recall@1=0.159` |
| 0.417 | `python measure_trust_set.py` | `Recall@3=0.417` |
| 0.515 | `python measure_trust_set.py` | `Recall@10=0.515` |
| 0.303 | `python measure_trust_set.py` | `MRR=0.303` |
| 0.295 | `python measure_trust_set.py` | `MRR@5=0.295` |
| 0.455 | `python measure_trust_set.py` | `Recall@5=0.455` |
| 66.7% | `python measure_trust_set.py` | `OOC refusal (n=15): 66.7%` |
| 0.0% | `python measure_trust_set.py` | `BOUNDARY refusal (n=10): 0.0%` |
| 27.3% | `python measure_trust_set.py` | `FALSE REFUSAL in-corpus (n=33): 27.3%` |
| 100.0% | `cat pilots/graphrag/eval/trust_set_report.md` | `OOC refusal: 15/15 (100.0%)` |
| 50.0% | `cat pilots/graphrag/eval/trust_set_report.md` | `BOUNDARY refusal: 5/10 (50.0%)` |
| 48.5% | `cat pilots/graphrag/eval/trust_set_report.md` | `FALSE REFUSAL in-corpus: 16/33 (48.5%)` |
| 15/15 | `cat pilots/graphrag/eval/trust_set_report.md` | `OOC refusal: 15/15 (100.0%)` |
| 5/10 | `cat pilots/graphrag/eval/trust_set_report.md` | `BOUNDARY refusal: 5/10 (50.0%)` |
| 16/33 | `cat pilots/graphrag/eval/trust_set_report.md` | `FALSE REFUSAL in-corpus: 16/33 (48.5%)` |
| 15/33 | `cat pilots/graphrag/eval/trust_set_report.md` | `TRAFIONE 15/33` |
| 18/33 | `cat pilots/graphrag/eval/trust_set_report.md` | `ZAWODNE 18/33` |
| 16/18 | `cat references/measurements.md` | `In 16 of 18 false refusals` |
| 88.9% | `cat references/measurements.md` | `family recall @5 = 88.9%` |
| 0% | `cat references/measurements.md` | `exact recall @5 = 0%` |
| 0.207 | `cat pilots/graphrag/eval/trust_set_report.md` | `MRR@5 0.207` |
| 0.242 | `cat pilots/graphrag/eval/trust_set_report.md` | `Recall@5 0.242` |
| 417 | `cat references/measurements.md` | `discarded 417 clean chunks` |
| 828 | `cat references/measurements.md` | `all 828 chunks of Paradigms` |
| 1123 | `cat references/measurements.md` | `all 1,123 of AIMA` |
| 11/386 | `cat references/measurements.md` | `gold still lands at 11/386` |
| 18/191 | `cat references/measurements.md` | `gold still lands at 18/191` |
| 76/210 | `cat references/measurements.md` | `gold still lands at 76/210` |

## not checked:
- czy nagłówek Recall@5 ma zniknąć ze stdout skryptu (wymaga decyzji właściciela KR).
- czy test set ma być rozszerzony o ranking wewnątrz rodziny (poza zakresem T7).
<!-- audit:end -->
