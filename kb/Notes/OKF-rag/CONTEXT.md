---
type: Concept
title: CONTEXT
description: Słownik artefaktów warstwy nawigacji i dowodu nad notatkami OKF-rag.
generated: { by: opencode, at: 2026-10-25T00:00:00Z }
---

# Notes/OKF-rag — CONTEXT.md

Ten kontekst opisuje, czym są artefakty warstwy nawigacji i dowodu nad
notatkami: co wskazuje drogę, co jest dowodem i co jest tylko wynikiem
wyszukiwania. To jest słownik; procedura retrieval mieszka w
`skills/retrieval-two-stage/` i `DECISION-kontrakt-odpowiedzi-retrieval.md`,
nie tutaj.

## Language

**Hub**:
Notatka kuratorska (`synthesis` albo `decision`), którą ranking semantyczny
zwraca pierwszą dla danego pytania. Punkt wejścia w nawigację, nigdy dowód.
_Avoid_: summary, index, mapa, strona docelowa

**Slice**:
Mała notatka pochodna niosąca jeden temat dużego importu, z `source`,
`source_lines` i krótkim excerptem. Pomoc nawigacyjna, nigdy dowód.
_Avoid_: chunk, fragment, wyciąg, podział

**Source**:
Plik, który zawiera dowód dla tezy. Hub ani slice nie są `source`.
_Avoid_: dokument, notatka, strona

**Locator**:
Pozycja wewnątrz `source`: nagłówek, anchor albo zakres linii.
_Avoid_: link, cytat, referencja

**Passage**:
Blok albo zakres zwrócony przez retrieval, ze statusem `exact` lub `related`.
Właściwość wyniku wyszukiwania, nie dowodu.
_Avoid_: snippet, chunk, trafienie

**`exact` / `related`**:
Dwie wartości statusu passage'u. `exact` leży w całości w zakresie gold.
`related` dotyka sekcji zakresu gold, ale nie musi zawierać zdania odpowiedzi —
dlatego wymaga ręcznej weryfikacji, zanim ktokolwiek go zacytuje.

**`evidence_status`**:
Czterowartościowy status tezy: `direct`, `supported`, `inferred`, `unknown`.
Definiuje go `DECISION-kontrakt-odpowiedzi-retrieval.md`; ten plik tylko
odsyła.
_Avoid_: confidence, related

**Gold** (zakres gold):
Zapisany plik i zakres linii, który musi zawierać odpowiedź. Ground truth
benchmarku.
_Avoid_: expected, odpowiedź, target

**Scope**:
Folder, do którego zawęża się zapytanie semantyczne. Slice'e są znajdowane
tylko przy scope zawężonym do `_slices/<source>/`; w całym `Notes/OKF-rag`
ranking przejmują huby.
_Avoid_: filtr, folder, zasięg
