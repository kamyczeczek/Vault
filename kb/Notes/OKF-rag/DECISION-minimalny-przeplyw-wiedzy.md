---
type: decision
title: Minimalny przepływ od materiału do decyzji
description: Roboczy sposób zamieniania surowych materiałów w koncepty, syntezy, decyzje i eksperymenty.
status: draft
tags: [knowledge-management, workflow, okf, vault]
sources:
  - { file: SYNTHESIS.md, lines: "34-154" }
  - { file: SPEC.md, lines: "159-245" }
  - { file: ontoship.md, lines: "271-330" }
  - { file: napkin.md, lines: "316-360" }
generated:
  by: codex
  at: 2026-10-25T00:00:00Z
---

# Kontekst

`Notes/OKF-rag` zawiera specyfikacje, importy repozytoriów i opisy narzędzi.
Materiały są wartościowe, ale nie wszystkie są rekomendacjami i nie wszystkie
powinny być redagowane. Bez rozdzielenia źródeł od wniosków porządkowanie łatwo
zamienia się w przenoszenie plików bez poprawy użyteczności.

# Problem

Potrzebny jest prosty przepływ, który odpowiada na cztery pytania:

- skąd pochodzi dana teza;
- czy jest faktem, syntezą czy hipotezą;
- co z niej wynika dla workspace'u;
- jaki następny krok pozwala ją sprawdzić.

# Decyzja

Przyjmujemy czterowarstwowy przepływ:

```text
surowy materiał
    → wybrane twierdzenia
    → koncept lub synteza ze źródłami
    → decyzja albo eksperyment
```

Zasady:

1. Istniejące importy pozostają korpusem źródłowym i nie są masowo przepisywane.
2. Każda trwała notatka ma typ, tytuł, jednozdaniowy opis, status i źródła.
3. Jedna synteza odpowiada na jedno pytanie, zamiast streszczać cały katalog.
4. Twierdzenia wyprowadzone z kilku źródeł oznaczamy jako `[inferred]`.
5. Synteza kończy się decyzją, eksperymentem albo jawną listą pytań otwartych.
6. Indeksy, grafy i wyszukiwarki są warstwą pochodną; Markdown pozostaje źródłem
   prawdy.

# Uzasadnienie

Ten przepływ łączy wspólne elementy opisane w [syntezie](SYNTHESIS.md):
czytelny Markdown jako źródło prawdy, metadane OKF jako interfejs wyszukiwania,
destylację według tematów oraz decyzje zapisane tak, aby nie trzeba było
ponownie rozstrzygać tego samego od zera.

# Konsekwencje

## Korzyści

- można zacząć od małej próbki bez reorganizacji całego vaultu;
- każda teza zachowuje pochodzenie i poziom pewności;
- łatwo odróżnić opis istniejącego narzędzia od decyzji dla własnego workspace'u;
- późniejsze indeksowanie może korzystać z ustabilizowanych konceptów.

## Koszty

- trzeba ręcznie wybrać pytanie i odróżnić fakt od interpretacji;
- pojawi się dodatkowa warstwa krótkich notatek obok materiałów źródłowych;
- status `draft` wymaga późniejszego przeglądu zamiast udawania pewności.

# Poza zakresem

Ta decyzja nie wybiera jeszcze między Obsidian CLI, Smart Connections, OKF-RAG,
llmwiki i napkin. Narzędzie ma wspierać przepływ, a nie zastępować decyzję o
tym, jaka wiedza jest trwała i użyteczna.

# Eksperyment walidacyjny

## Próba

Użyć trzech źródeł:

- [SPEC](SPEC.md) — kontrakt formatu;
- [OntoShip](ontoship.md) — organizacja i zapis decyzji;
- [Napkin](napkin.md) — destylacja i utrzymanie.

Na ich podstawie utrzymać tę decyzję jako jeden dokument i sprawdzić, czy można
odpowiedzieć na pytania:

1. Co jest źródłem prawdy?
2. Jak odróżnić surowy materiał od konceptu?
3. Co robimy z nowym wnioskiem?

## Kryterium sukcesu

Eksperyment jest udany, jeśli czytelnik potrafi wskazać źródło każdej ważnej
tezy, odróżnić fakt od `[inferred]` i wykonać następny krok bez ponownego
czytania całych importów.

## Warunek rewizji

Po przetworzeniu 3–5 kolejnych materiałów sprawdzimy, czy ten sam przepływ
powtarza się bez wyjątków. Jeśli nie, zmienimy decyzję lub dodamy osobny typ
notatki; nie będziemy rozszerzać schematu tylko po to, aby obsłużyć pojedynczy
przypadek.
