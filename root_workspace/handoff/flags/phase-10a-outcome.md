---
flag: phase-10a-outcome
since: 2026-10-11
owner: mateusz
agent: pi
model: gemini/gemini-flash-lite-latest
origin: test hipotezy tłumaczenia PL→EN przed retrievalem (Faza 10A)
---

## Stan

Zmierzyliśmy empirycznie wpływ tłumaczenia PL→EN na retrieval, na 4 grupach pytań (in-corpus PL, OOC PL, canary, in-corpus EN). Pomiar wykonany na wersji pilota z Fazy 8S (bez modyfikacji kodu).

**Liczby (baseline → translated):**
- In-corpus PL (12): MRR@5 0.507 → 0.778, Recall@5 0.708 → 0.875
- OOC PL (5): refusal 5/5 → 1/5
- Canary (5): refusal 5/5 → 1/5
- In-corpus EN (8): MRR@5 0.771 → 0.771 (kontrola)

**Wniosek z pomiaru:**
Tłumaczenie zapytań PL na EN znacząco poprawia MRR@5 i Recall@5 na korpusie (z 0.507 do 0.778), ale drastycznie obniża odporność na pytania out-of-corpus oraz canary (z 5/5 refusals do 1/5), co dowodzi, że tłumaczenie gubi sygnał nieznajomości i powoduje hallukynacje/falsse positive retrievala.

**Pliki:**
- Raport pomiarowy: docs/phase-10a-translation-experiment.md
- Surowe artefakty: reports/phase10a/phase10a_results.json

## Czego NIE zweryfikowano
- Koszt latencji tłumaczenia.
- Zachowanie na pełnym korpusie.
- Czy tłumaczenie pomaga OOC EN.

## Rekomendacja dla właściciela
Nie wprowadzać globalnego tłumaczenia PL→EN przed retrievalem ze względu na zniszczenie mechanizmu refusalu (canary/OOC).
