# Retrieval paradox — 0.938 vs 0.295 (2026-10-14)

<!-- audit:begin -->
## Pytanie
Czy `mean_family_recall = 0.938` (`references/measurements.md`) i MRR@5 = 0.295
(Trust Set, `measure_trust_set.py`) mierzą to samo, czy coś innego?
Trzy odpowiedzi: A (błąd w jednej liczbie), B (ten sam pomiar na różnych zbiorach),
C (różne metryki).

## Co produkuje 0.938
Skrypt `run_retrieval_benchmark.py` (ARL, `knowledge/graph/`, CHECK z GATES.md G1)
na zbiorze `retrieval_benchmark.json` o rozmiarze 8 przypadków (EN), pipeline
`ask.query` z limitem 5. Definicja metryki (linie 18-20 i 87-94 skryptu,
verbatim w sensie logicznym):

```
family(id) = re.sub(r"^\d+_", "", id)          # pasek liczbowy = rodzina = slug
family_recall = |gold_families ∩ retrieved_families| / |gold_families|
mean_family_recall = średnia po 8 przypadkach
```

Trafienie = JAKIKOLWIEK chunk tego samego sluga w top 5, bez wagi pozycji.
Artefakt `retrieval_benchmark_results.json` (status VALID): `mean_family_recall`
0.938, `mean_concept_coverage` 1.0, `mean_family_precision` 0.654,
`mean_exact_recall` 0.312, `mean_latency_ms` 100.188. Kluczowy wiersz dowodowy:
w 5 z 8 przypadków `exact_recall` wynosi 0 przy `family_recall` 1.0
(przykład: gold `25_the_book_of_why...`, hit `40_the_book_of_why...` —
ten sam slug, inny numer chunka).

## Co produkuje 0.295
Skrypt `measure_trust_set.py` (linie 30-58) na 58 pytaniach z `questions.md`:
33 in-corpus, 15 out-of-corpus, 10 boundary. Pipeline: `zbuduj_plan` +
`retrieve` z hybrydą ON (`plan.uzyj_wektorow = True`, linia 34), `oblicz_pokrycie`
bez `pytanie=` (semantic OFF, linia 37). Definicja metryki (`graphrag.py`,
linie 426-437):

```
mrr_at_k(oracle, ranked, k=5) = 1/rank pierwszego EXACT-ID trafienia w top 5
brak exact-ID trafienia -> 0.0
```

Agregat liczony tylko na 33 pytaniach in-corpus (linie 78-88). Artefakt
`trust_set_results.json` daje: MRR@5 0.295, MRR (k=10) 0.303, recall@5 0.455,
family_recall@5 0.939, NDCG@5 0.336, false refusal 27.3%, OOC refusal 66.7%,
boundary refusal 0.0%.

## Porównanie
| Wymiar | 0.938 (benchmark) | 0.295 (Trust Set) |
|---|---|---|
| Metryka | family_recall: dowolny chunk sluga = hit, bez wagi rangi | MRR@5: exact chunk-ID + waga 1/rank |
| Test set | 8 przypadków EN (`retrieval_benchmark.json`) | 33 in-corpus PL (+15 OOC +10 boundary = 58) |
| Pipeline | `ask.query`, limit 5, korpus ARL | `graphrag.retrieve`, hybryda ON, semantic OFF |
| Surowość | lenient | strict (kara za defect class 4: re-ingest zmienia numery chunków) |

Rozstrzygający eksperyment bez nowego kodu — ta sama lenient metryka na Trust
Secie: `family_recall@5` na 33 pytaniach in-corpus wynosi 0.939, czyli jest
równa 0.938 z benchmarku co do 0.001. Luka 0.938 vs 0.295 istnieje w całości
MIĘDZY metrykami na tym samym materiale (rodzina vs exact-ID z rangą), a nie
między zbiorami. Zbiory też są różne (8 EN vs 33 PL), ale to nie one niosą lukę:
dowód w obie strony — (a) w benchmarku 5 z 8 przypadków ma exact 0 przy family
1.0; (b) na Trust Secie family 0.939 przy MRR 0.295.

## Wniosek
C — mierzą co innego. `mean_family_recall` to trafienie w rodzinę (slug),
MRR@5 to trafienie w exact chunk-ID z premią za rangę; obie liczby są poprawne
w swoich definicjach i nie ma sprzeczności ani błędu. Myląca jest etykieta w
`measurements.md`, która zestawia je bez jawnego ostrzeżenia o surowości.
Odpowiedź na „mamy sprawny retrieval?": NIE WIEM z jednego zdania —
retriever trafia we właściwy dokument w 93.9% (family), ale w exact chunk
z dobrą rangą tylko w 29.5% (MRR@5); pilot terminated, gate 0.4 oblany.

## Co dalej
Jedno zdanie: właściciel decyduje, czy bramką ma być family_recall (wtedy
retrieval sprawny) czy MRR@5 (wtedy nie) — bez tej decyzji każda kolejna sesja
będzie zgadywaniem; kodu nie zmieniano, ticketu nie otwierano (odpowiedź C).

## Tool calls
| Wartość | Komenda | Surowy output (fragment) |
|---|---|---|
| 0.938, 1.0, 0.654, 0.312, 100.188, 8 | `python scripts/_scratch/paradox_bench.py` | `mean_family_recall: 0.938 ... cases: 8 ... mean_concept_coverage: 1.0 ... mean_family_precision: 0.654 ... mean_exact_recall: 0.312 ... mean_latency_ms: 100.188` |
| 8 (spec) | `python -c "import json; ... retrieval_benchmark.json ... len(d['cases'])"` | `spec_cases=8` |
| 5 z 8 | `python scripts/_scratch/paradox_bench.py` | `exact_zero_family_one=5/8` |
| 58, 33, 15, 10 | `python scripts/_scratch/paradox_agg.py` | `n_total=58 n_in=33 n_ooc=15 n_bnd=10` |
| 0.295 | `python scripts/_scratch/paradox_agg.py` | `mean_mrr@5=0.295` |
| 0.303 | `python scripts/_scratch/paradox_agg.py` | `mean_mrr=0.303` |
| 0.455 | `python scripts/_scratch/paradox_agg.py` | `mean_recall@5=0.455` |
| 0.939 | `python scripts/_scratch/paradox_agg.py` | `mean_family_recall@5=0.939` |
| 0.336 | `python scripts/_scratch/paradox_agg.py` | `mean_ndcg@5=0.336` |
| 27.3% | `python scripts/_scratch/paradox_agg.py` | `false_refusal=27.3%` |
| 66.7% | `python scripts/_scratch/paradox_agg.py` | `ooc_refusal=66.7%` |
| 0.0% | `python scripts/_scratch/paradox_agg.py` | `bnd_refusal=0.0%` |
| 0.001 | `python scripts/_scratch/paradox_agg.py` + `paradox_bench.py` (0.939 − 0.938) | `0.939` vs `0.938` — różnica wyliczona z obu wierszy powyżej |
| 5 (limit) | `measure_trust_set.py` linia 54 / `run_retrieval_benchmark.py` linia 81 (`limit=5`) | `mrr_at_k(..., 5)`, `ask.query(case["query"], limit=5, recall=True)` |
| 0.4 (gate) | `references/measurements.md` + flaga kr-pilot-terminated (MRR@5=0.295 < 0.4) | `MRR@5=0.295 < 0.4 (gate oblany 4. raz)` z mapy, wpis KR-pilot-terminated-2026-10-14 |
| 29.5%, 93.9% | przeformułowanie 0.295 / 0.939 z wierszy powyżej | ten sam output `paradox_agg.py` |
| 82586 B (HANDOFF przed) | `Get-Item HANDOFF.md \| Select-Object Length` | `82586` |
| 0 (otwarte tickety) | `Select-String -Path docs/wayfinder-retrieval-map.md -Pattern "\| open \|"` (brak trafień) | brak wierszy `\| open \|` — wszystkie tickety closed/closed-not-reached |

## not checked:
- Czy właściciel wybiera family_recall czy MRR@5 jako bramkę docelową.
- Czy `mean_latency_ms` 100.188 (artefakt) vs 99.4 (measurements.md) to inny run czy zaokrąglenie — poza zakresem (nie wpływa na wniosek C).

<!-- audit:end -->
