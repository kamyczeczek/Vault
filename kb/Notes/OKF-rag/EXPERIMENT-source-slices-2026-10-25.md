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

# Follow-up: Napkin Q14–Q16

Wygenerowano trzy deterministyczne slice'y z `napkin.md`: `Distill —
Conversation to Vault` (3774–3915), `Tend — Vault Upkeep` (3916–3998) oraz
`Agent Memory System — Progressive Disclosure` (3094–3147). Wszystkie trzy
mają aktualny `origin_hash` w manifeście i własne wpisy w indeksie `_slices`.

## Metoda

Dla Q14–Q16 użyto trzech wariantów: pytania naturalnego, pytania z nazwą
Napkin i terminami sekcji oraz dokładnego nagłówka. Wektory zapytań utworzono
aktywnym modelem Smart Connections `TaylorAI/bge-micro-v2` (384 wymiary), a
wyniki policzono cosine similarity nad 364 osadzonymi blokami w
`Notes/OKF-rag`. Ranking plików to najwyższy wynik bloku danego pliku;
zastosowano `top 10` i próg `min_score=0.55`.

| Q | Wariant i zapytanie | Ranga pliku docelowego | Score |
|---|---|---:|---:|
| Q14 | Naturalne: `How do I distill valuable knowledge from an agent conversation into the vault?` | 1 | 0.7733 |
| Q14 | Nazwane: `Napkin distill conversation to vault: gate, extract knowledge, cluster by topic, merge an existing note or create a new note, then verify.` | 2 | 0.8583 |
| Q14 | Nagłówek: `Distill — Conversation to Vault` | 1 | 0.7834 |
| Q15 | Naturalne: `How should I inspect and conservatively tend a knowledge vault, fix broken links, handle tags and orphans, and verify?` | 1 | 0.7969 |
| Q15 | Nazwane: `Napkin Tend Vault Upkeep: inspect unresolved links, orphans, tag sprawl, prioritize a few safe issues, and verify changes.` | 1 | 0.8619 |
| Q15 | Nagłówek: `Tend — Vault Upkeep` | 1 | 0.7424 |
| Q16 | Naturalne: `How does Napkin keep an agent context small by revealing memory gradually through pinned context, maps, snippets, and full reads?` | 1 | 0.7909 |
| Q16 | Nazwane: `Napkin agent memory progressive disclosure: level 0 pinned context, level 1 overview map, level 2 search snippets, level 3 read.` | 1 | 0.8684 |
| Q16 | Nagłówek: `Agent Memory System — Progressive Disclosure` | 1 | 0.8398 |

Wszystkie dziewięć wyników umieściło właściwy slice w top 2 i powyżej progu.
Wyjątkiem ranką pozostaje Q14 wariant nazwany: lokalny indeks Napkin zajął
miejsce 1 z wynikiem 0.8607, a właściwy slice miejsce 2 z 0.8583. Q15 i Q16
trafiły do właściwego slice'a na miejscu 1 we wszystkich wariantach.

## Stan indeksu

W `Notes/OKF-rag` 36/36 plików Markdown ma odpowiadający wpis w Smart Sources;
nie znaleziono brakujących ani nieistniejących ścieżek. Odczytano poprawnie
wszystkie 453 zapisane wektory źródeł i 2446 wektorów bloków (384 wymiary,
0 niepoprawnych). Adapter nie zgłasza aktywnego błędu ani zatrzymanej kolejki.
W logu zdarzeń został jeden historyczny wpis `embedding:error`; poprzednie
ostrzeżenie o 15 nieczytelnych wektorach nie powtórzyło się w aktualnym
odczycie. Nie wykonano pełnego reindeksu, bo kontrola ścieżek i wektorów
przeszła bez błędów.

# Następny krok

Jeśli potrzebne jest porównanie wpływu na cały korpus, powtórzyć benchmark
20 pytań na aktualnym indeksie. Kolejnych importów nie dzielić bez
powtarzalnego missu i stabilnego zakresu źródła.
