---
type: decision
title: Kontrakt odpowiedzi retrieval
description: Minimalny format łączący tezę z dowodem, cytatem i poziomem pewności.
status: draft
tags: [okf-rag, retrieval, evidence, citations]
sources:
  - { file: EXPERIMENT-retrieval-benchmark-20-2026-10-25.md, lines: "33-80" }
  - { file: EXPERIMENT-retrieval-raw-only-2026-10-25.md, lines: "41-85" }
  - { file: EXPERIMENT-retrieval-misses-2026-10-25.md, lines: "22-73" }
  - { file: SYNTHESIS-kompilacja-i-wyszukiwanie.md, lines: "37-134" }
generated:
  by: codex
  at: 2026-10-25T00:00:00Z
---

# Cel

Retrieval ma nie tylko znaleźć podobny tekst. Ma pozwolić odpowiedzieć na
trzy pytania:

1. jaka jest teza;
2. z którego pliku i fragmentu pochodzi;
3. czy odpowiedź jest bezpośrednio potwierdzona, wywnioskowana czy nieznana.

Smart Connections służy do znalezienia konceptu lub huba. Nie traktujemy jego
rankingu jako dowodu ani jako systemu cytowania.

# Kontrakt

Każda odpowiedź oparta na vaultcie powinna mieć strukturę:

```text
claim → source → locator → passage → evidence_status → confidence
```

| Pole | Wymaganie |
|---|---|
| `claim` | Jedno konkretne twierdzenie, bez mieszania kilku wniosków. |
| `source` | Ścieżka do pliku źródłowego, nie tylko do syntezy. |
| `locator` | Nagłówek, blok, zakres linii albo inny stabilny punkt zaczepienia. |
| `passage` | Krótki cytat lub precyzyjne streszczenie fragmentu. |
| `evidence_status` | `direct`, `supported`, `inferred` albo `unknown`. |
| `confidence` | `high`, `medium` albo `low`, z krótkim uzasadnieniem. |

Brak `source` i `locator` oznacza, że teza nie jest jeszcze gotowa do
trwałej odpowiedzi.

# Poziomy dowodu

## `direct`

Źródło zawiera tezę wprost. Odpowiedź może użyć faktu, ale powinna wskazać
plik i fragment.

## `supported`

Źródło nie zawiera dokładnego zdania, ale zawiera wystarczająco bliski materiał
do ostrożnego podsumowania. Należy zaznaczyć, że jest to parafraza.

## `inferred`

Wniosek powstaje z co najmniej dwóch fragmentów albo z połączenia faktu
ze skutkiem projektowym. Trzeba wymienić przesłanki i nie przedstawiać wniosku
jako cytowanego faktu.

## `unknown`

Nie znaleziono wystarczającego dowodu. Odpowiedź powinna odmówić rozstrzygnięcia
albo wyraźnie oznaczyć hipotezę do sprawdzenia. Sąsiedni, podobny dokument nie
jest substytutem dowodu.

# Przepływ wyszukiwania

```text
1. sklasyfikuj pytanie
2. znajdź koncept lub syntezę semantycznie
3. przejdź z huba do pliku źródłowego
4. zweryfikuj fragment przez FTS5, rg albo odczyt źródła
5. zapisz claim, locator, passage i status dowodu
6. odpowiedz albo odmów
```

Routing:

- pytanie o sens lub parafrazę: Smart Connections jako generator kandydatów;
- nazwa, fraza, nagłówek lub dokładny cytat: FTS5 albo `rg`;
- pochodzenie, kolejność i zależność: graph retrieval;
- brak potwierdzenia po weryfikacji: `unknown`, nie synteza z podobnych wyników.

Wynik semantyczny może prowadzić do źródła, ale dopiero weryfikacja źródła
może podnieść status tezy powyżej `unknown`.

# Source slices

Dla dużych, heterogenicznych importów dopuszczamy małe notatki pochodne typu
`source-slice`. Slice powinien zawierać jeden temat, krótki excerpt oraz jawne
`source` i `source_lines`. Jest pomocą nawigacyjną, a nie nowym źródłem prawdy.

Slice tworzymy dopiero po powtarzalnym miss retrieval, kiedy znamy temat i
stabilny zakres źródła. Po znalezieniu slice'a odpowiedź nadal weryfikuje
oryginalny plik przez FTS5, `rg` albo bezpośredni odczyt. Nie dzielimy masowo
całego vaultu i nie awansujemy excerptu do `direct` bez sprawdzenia źródła.

# Format odpowiedzi

Minimalny format dla jednej tezy:

```markdown
### Teza

<jedno zdanie>

- Status: `direct` | `supported` | `inferred` | `unknown`
- Źródło: `Notes/OKF-rag/<plik.md>`
- Lokalizator: `<nagłówek / blok / linie>`
- Dowód: “<krótki cytat lub precyzyjna parafraza>”
- Pewność: `high` | `medium` | `low` — <uzasadnienie>
```

Dla kilku tez każda teza dostaje osobny rekord. Nie wolno używać jednego
cytatu jako pozornego uzasadnienia dla całej syntezy.

# Bramka jakości

Odpowiedź przechodzi bramkę, jeśli:

- każda ważna teza ma źródło i lokalizator;
- cytat rzeczywiście wspiera tezę, a nie tylko pochodzi z tego samego pliku;
- `inferred` wymienia swoje przesłanki;
- odpowiedź spoza korpusu kończy się jawnym `unknown` lub odmową;
- wynik można odtworzyć bez ponownego czytania całego importu.

Metryki benchmarku powinny osobno mierzyć: source recall, passage precision,
exact/related passage, poprawność cytowania, refusal dla out-of-corpus oraz
wpływ języka zapytania. Samo znalezienie właściwej rodziny pliku nie wystarcza.

# Decyzja i zakres rewizji

Przyjmujemy ten kontrakt jako warstwę odpowiedzi nad istniejącym korpusem.
Nie wymaga on masowego dzielenia `napkin.md`, `okf-rag.md` ani `okforge.md`;
dopuszcza tylko targeted source slices dla powtarzalnych missów. Rewizja będzie
potrzebna, jeżeli pięć kolejnych realnych pytań wykaże, że lokalizator lub
poziomy dowodu są niewystarczające.

# Źródła decyzji

- [Benchmark: plik i fragment źródłowy](EXPERIMENT-retrieval-benchmark-20-2026-10-25.md)
- [Control: raw-only](EXPERIMENT-retrieval-raw-only-2026-10-25.md)
- [Kontrola brakujących trafień](EXPERIMENT-retrieval-misses-2026-10-25.md)
- [Synteza: kompilacja i wyszukiwanie](SYNTHESIS-kompilacja-i-wyszukiwanie.md)
