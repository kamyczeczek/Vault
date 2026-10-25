---
type: experiment
title: Source slices dla dużych importów
description: Kontrolowany test małych, pochodnych slice'ów jako warstwy nawigacyjnej retrieval.
status: complete
tags: [okf-rag, retrieval, source-slices, benchmark]
sources:
  - EXPERIMENT-retrieval-misses-2026-10-25.md
  - DECISION-kontrakt-odpowiedzi-retrieval.md
  - okf-rag.md
  - ../../scripts/generate_source_slices.py
  - ../../scripts/source_slice_specs/okf-rag.json
generated:
  by: codex
  at: 2026-10-25T00:00:00Z
---

# Pytanie

Czy małe, tematyczne notatki pochodne mogą naprawić nawigacyjny retrieval dla
dużych, heterogenicznych importów bez przepisywania źródła?

# Hipoteza

Jeśli problemem jest konkurencja wielu tematów w jednym pliku, to source slice
z jednym tematem, metadanymi `source` i `source_lines` oraz krótkim excerptem
powinien być łatwiejszy do znalezienia semantycznie. Slice nie będzie dowodem
sam w sobie; ma prowadzić do oryginalnego pliku i lokalizatora.

# Przygotowanie

Slice'y są generowane przez `scripts/generate_source_slices.py` na podstawie
specyfikacji `scripts/source_slice_specs/okf-rag.json`. Wynik trafia do
`Notes/OKF-rag/_slices/okf-rag/`, razem z `manifest.json`.

Generator wybiera pięć tematów przez nagłówki lub stabilne markery tekstowe:

- proposal-to-truth — `okf-rag.md:445–448`;
- pipeline state — `okf-rag.md:461–475`;
- end-to-end flow — `okf-rag.md:231–266`;
- benchmark metrics — `okf-rag.md:573–602`;
- extraction findings — `okf-rag.md:1134–1141`.

Każdy slice ma `origin`, `origin_hash`, `source_lines`, `source_heading`,
`slice_hash` i wersję generatora. Oryginalny `okf-rag.md` nie został zmieniony.
Wcześniejsze ręczne prototypy zostały usunięte, aby nie utrzymywać drugiej kopii.

Po kontrolowanym restarcie Obsidiana indeks Smart Connections nadal ładował
stare wektory, dlatego wykonano oficjalne `smart_sources.reindex_embeddings()`
przez Obsidian CLI. Reindeks przetworzył 646 źródeł, wyczyścił 449 aktywnych
referencji źródeł i 2421 referencji bloków. Stan po operacji: `450` notatek,
`2422` bloki, `stale_notes=0`, `stale_blocks=0`; model i wymiary pozostały
`TaylorAI/bge-micro-v2` / `384`. Usunięte prototypy nie wracają do wyników.

W vaultcie pozostał pusty `Notes/OKF-rag/source-slices/index.md`, który Obsidian
automatycznie odtwarza jako indeks folderu; nie zawiera on ręcznych prototypów.

# Metoda

Użyto tych samych pięciu przypadków Q06–Q10, które wcześniej nie znalazły
`okf-rag.md` w raw-only top-10. Dla każdego pytania zapytano Smart Connections
semantycznie, najpierw w folderze slice'ów, a następnie w całym
`Notes/OKF-rag`, przy `scope=blocks`, `top 10` i `min_score=0.55`.

To testuje nawigację do tematu. Nie jest to jeszcze pomiar exact passage
precision ani dowód, że slice zastąpi weryfikację w źródle.

Generator i jego walidacja:

```text
python scripts/test_generate_source_slices.py                 → 3/3 tests OK
python scripts/generate_source_slices.py --check              → OK
```

# Wyniki

| ID | Cel | Score | Rank w slice folder | Rank w całym `Notes/OKF-rag` |
|---|---|---:|---:|---:|
| Q06 | `okf-rag--proposal-to-truth.md` | 0.7274 | 1 | — |
| Q07 | `okf-rag--proposal-to-truth.md` | 0.6366 | 1 | — |
| Q08 | `okf-rag--end-to-end-flow.md` | 0.6917 | 1 | — |
| Q09 | `okf-rag--benchmark-metrics.md` | 0.6465 | 1 | — |
| Q10 | `okf-rag--extraction-findings.md` | 0.6025 | 2 | — |

Świeży wynik nawigacyjny generatora: `4/5` top-1 i `5/5` top-5 w folderze
`Notes/OKF-rag/_slices/okf-rag`. Dla porównania wcześniejszy raw-only test miał
`0/5` oczekiwanych `okf-rag.md` w top-10 dla tych przypadków.

Po reindeksie żaden z pięciu slice'ów nie trafił do top-10 przy wyszukiwaniu w
całym `Notes/OKF-rag`: tam ranking nadal przejmują syntezy, decyzje i raporty.
To pokazuje, że slice'y są skuteczną warstwą źródłową po zawężeniu folderu, ale
nie zastępują globalnego rankingu kuratorowanych hubów.

# Weryfikacja dowodu

Po znalezieniu slice'a lokalizator prowadził do oryginalnego źródła:

| ID | Oryginalny locator | Status dowodu |
|---|---|---|
| Q06 | `okf-rag.md:445–447` | `direct` |
| Q07 | `okf-rag.md:445–447` | `direct` |
| Q08 | `okf-rag.md:231–260` | `direct` |
| Q09 | `okf-rag.md:573–583` oraz `1022–1032` | `direct` |
| Q10 | `okf-rag.md:1134–1140` | `direct` |

Weryfikacja nadal odbywa się w źródle przez `rg` albo odczyt wskazanego zakresu.
Slice poprawia odkrycie, ale nie podnosi automatycznie statusu dowodu.

# Werdykt

Hipoteza nawigacyjna przechodzi warunkowo. Generowane source slices są skuteczną,
małą warstwą pośrednią dla dużego importu, gdy retrieval jest ograniczony do
folderu slice'ów. Nie uzasadnia to masowego dzielenia całego vaultu ani
zastępowania źródła slice'ami.

Przyjmujemy regułę:

```text
powtarzalny miss dużego importu
→ mały source slice z source + source_lines + excerpt
→ Smart Connections znajduje slice w scoped source folder
→ lexical/direct read weryfikuje oryginał
```

Nie tworzymy slice'a dla każdego pliku z góry. Tworzymy go dopiero po
powtarzalnym missie, gdy znany jest konkretny temat i stabilny zakres źródła.

# Ograniczenia

- próba ma pięć przypadków i używa kontrolowanych rekonstrukcji pytań;
- mierzy top-1 nawigacji, nie pełną jakość odpowiedzi;
- slice może zestarzeć się po zmianie źródła, więc `source_lines` wymagają
  okresowej kontroli;
- indeks Smart Connections jest warstwą pochodną i nie jest źródłem prawdy.

# Następny krok

Zastosować tę regułę do jednego innego dużego importu, najlepiej `napkin.md`,
i sprawdzić, czy jeden lub dwa slice'y wystarczą do odzyskania Q14–Q16.
