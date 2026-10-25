---
type: Concept
title: ADR-001-single-brain-db
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# ADR-001: Jedna baza brain.db jako źródło prawdy

## Status
Zatwierdzony

## Kontekst
W dotychczasowej historii workspace'u wystąpił poważny problem duplikacji baz danych, rozproszonych magazynów pamięci, stanów sesji i plików indeksów wektorowych/tekstowych, co prowadziło do niespójności, braku synchronizacji i zagubienia wiedzy.

## Decyzja
Wprowadzamy jedną, centralną bazę SQLite `brain/brain.db` jako jedyne źródło prawdy (Single Source of Truth) dla:
1. Indeksów wiedzy i grafu powiązań.
2. Historii problemów i lekcji (`brain/problems/`, `brain/lessons.md`).
3. Metadanych sesji i transkryptów.

Wszelkie pochodne indeksy (np. FTS5, cache wyszukiwania) są generowane automatycznie ze skryptów narzędziowych na bazie `brain.db` i nigdy nie są edytowane ręcznie.

## Konsekwencje
- Likwidacja rozproszonych baz i JSON-ów magazynowych w różnych katalogach.
- Jasny kontrakt dostępu przez skrypty narzędziowe (`tools/memory/`).
- Wymóg aktualizacji indeksu po każdej modyfikacji kodu lub wiedzy.
