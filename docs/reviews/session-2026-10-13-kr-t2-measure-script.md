# Raport T2: Co mierzy `measure_trust_set.py`

## 1. Surowe outputy grep i read

### Grep:
```bash
grep -n "uzyj_wektorow" projects/research/knowledge-retrieval/pilots/graphrag/eval/measure_trust_set.py
```
Output:
```text
34:    plan.uzyj_wektorow = True  # hybryda ON
```

### Read (`measure_trust_set.py` fragment, linie 28-40):
```python
K = 10
results = []
for q in questions:
    plan = g.zbuduj_plan(q["pytanie"])
    plan.uzyj_wektorow = True  # hybryda ON
    wyniki = g.retrieve(plan, [])
    ranked = [w["id"] for w in wyniki]
    pokryte = g.oblicz_pokrycie(wyniki, plan.slowa_kluczowe)  # semantic OFF
    wynik = g.syntezuj_odpowiedz(q["pytanie"], pokryte)
```

## 2. Jednoznaczna odpowiedź

`measure_trust_set.py` mierzy hybrydę (FTS5 + wektory), bo linia 34 ustawia `plan.uzyj_wektorow = True` i wywołuje `g.retrieve(plan, [])`.

## 3. Weryfikacja braków CrossEncoder
Szukanie CrossEncoder w pliku zwróciło 0 trafień (brak rerankingu CrossEncoder).
