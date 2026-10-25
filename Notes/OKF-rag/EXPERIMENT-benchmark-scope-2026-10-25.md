---
type: experiment
title: Scope rule vs leaky related — pre-registered
description: Zapowiedziany przed przebiegiem test reguły scope i przypadku adwersaryjnego dla metryki related.
status: planned
blocked_on: runner nie ma trybu scoped — patrz §Blocker
tags: [okf-rag, retrieval, benchmark, metric-design, pre-registered]
sources:
  - EXPERIMENT-retrieval-benchmark-20-2026-10-25.md
  - EXPERIMENT-source-slices-2026-10-25.md
  - benchmark-questions.json
  - ../../scripts/run_okf_rag_benchmark.py
  - ../../SCARS.md
generated: { by: opencode, at: 2026-10-25T00:00:00Z }
---

# Status

**Pre-registered.** Ten plik powstał przed przebiegiem i nie wolno go edytować
po jego starcie — wolno dopisywać wyłącznie sekcje `# Wynik` i `# Werdykt`.
Powód: `SCARS.md:11` (metric-design scar) wymaga, żeby każda metryka
przeduruchomieniowa miała *zapisany* przypadek adwersaryjny — odpowiedź, która
przechodzi metrykę, a nie przechodzi merytorycznie. Metryka bez takiego
przypadku jest leaky, a interpretacja dobierana po wyniku nie jest pomiarem.

# Pytanie

Czy zawężenie zapytania do folderu źródłowego (reguła `scope` ze skilla
`retrieval-two-stage`) domyka pozostałe missy Q02 i Q20 — i czy przy tym
`any_exact_or_related@10 = 20/20` jest metryką godną bramkowania?

# Hipoteza

Scope naprawia nawigację: slice'y dowiodły `5/5` top-5 tylko po zawężeniu do
`_slices/<source>/`, a w całym `Notes/OKF-rag` nie weszły do top-10. Jeśli
Q02 (`SPEC.md:167–214`) i Q20 (`okf-generator.md:71–84`) nadal nie trafiają po
zawężeniu, problemem jest segmentacja bloków, nie brak slice'a.

# Co testujemy

Reguła: dla źródła większego niż ~200 KB najpierw pytaj
`Notes/OKF-rag/_slices/<source>/`, potem weryfikuj locator w oryginale.
Korpus, gold set i hash bez zmian:

- `Notes/OKF-rag/benchmark-questions.json`, 20 pytań + OOC01
- `corpus_sha256 = 2f0491bd350a5a5f88738726bb282dd61cfd0800bd8cc23543d333635953f046`
  (39 plików Markdown; runner sam odrzuci przebieg, jeśli hash się rozjedzie)

# Metryki pre-registered

Primary, bramkowane:

1. `exact@10 ≥ 15/20` — twardy cel.
2. `any_exact_or_related@10 = 20/20` — **warunkowo**, bo jest leaky (patrz
   przypadek adwersaryjny). Każdy passage `related` przechodzący próg ma
   ręczną adnotację „zawiera zdanie odpowiedzi: tak/nie”. Bez adnotacji wynik
   `related` nie liczy się do progu.

Secondary, zapisywane, nie bramkowane: `source_recall@10`,
`citation_target_correct@1`, `citation_target_valid@1`, abstention na OOC01.

# Przypadek adwersaryjny (zapisany przed przebiegiem)

**Q15** — „How does Napkin tend vault upkeep and prioritize the issues it
finds?” · gold `napkin.md:3916–3983`.

Obecny przebieg (`benchmark-results-20.json`, tryb `all`) zwrócił jako
`related` blok `napkin.md:3985–3998`, czyli `## Step 4: Verify and report`.
Blok zaczyna się **dwie linie po końcu zakresu gold** i zawiera krok
weryfikacji, a nie priorytetyzację, o którą pyta pytanie. Mimo to spełnia
definicję `related` (mieści się w sekcji obejmującej zakres gold) i zalicza
`any_exact_or_related@10`.

Oczekiwany wynik: **metryka go zalicza, ręczna weryfikacja odrzuca.**

Przypadek wspierający, ten sam wzorzec: **Q14** — gold `napkin.md:3774–3900`,
zwrócony `related` blok `napkin.md:3892–3915` (`## Step 6: Report`) — ogon
sekcji, nie metoda destylacji. Dwa z dziesięciu `related` to ogony procedury,
więc wzorzec jest systematyczny, nie jednostkowy.

# Reguła decyzyjna (pre-registered)

- Jeśli przypadek adwersaryjny się potwierdzi: `any@10` **przestaje** być
  celem bramkowanym, a wynik rozstrzyga `exact@10 ≥ 15/20`. Zaostrzenie samej
  definicji `related` (wymóg zdania odpowiedzi) to **osobny** eksperyment z
  własnym przypadkiem adwersaryjnym — nie poprawka po fakcie.
- Jeśli `exact@10 ≥ 15/20` i wszystkie `related` przechodzą ręczną adnotację:
  luka domknięta, żadnej zmiany toolingu.
- Jeśli `exact@10 < 15/20`: decyzja o toolingu (krok 5 planu), **nie**
  poluzowanie metryki.
- Jeśli Q02 i Q20 nadal miss po zawężeniu scope: problem segmentacji bloków,
  nie nawigacji; slice dla pojedynczego missa nadal łamie regułę „slice tylko
  po powtarzalnym missie”.

# Blocker

`scripts/run_okf_rag_benchmark.py` ma tryby `all`, `raw_only`, `both` i nie ma
trybu `scoped`. Reguła scope jest dziś instrukcją w skillu, nie mierzalnym
trybem, więc ten eksperyment **nie jest jeszcze uruchamialny jedną komendą**.
Przed przebiegiem trzeba dodać `scoped` do runnera (scope per źródło: folder
slice'ów, gdy istnieje, inaczej plik źródłowy). Bez tego pomiar byłby ręczny —
a ręczny przebieg nie jest pre-registered, bo nie da się go powtórzyć z tego
samego hasha.

# Komenda docelowa

```text
python scripts/run_okf_rag_benchmark.py --mode scoped \
    --output Notes/OKF-rag/benchmark-results-scope-2026-10-25.json
```

# Czego nie mierzymy

- treści generowanej odpowiedzi ani literalnej poprawności cytatu;
- pełnego passage precision poza top-10;
- świeżości slice'ów poza `origin_hash` (starzenie się `source_lines` przy
  edycji źródła nie jest wykrywane semantycznie);
- języka zapytania jako zmiennej (wszystkie pytania w jednym języku).
