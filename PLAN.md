# PLAN.md — Plan Przebudowy Workspace'u

## Cel przebudowy
Zbudowanie małego, spójnego, jednokierunkowego rdzenia opartego na Metodologii Interpretowalnego Kontekstu (ICM), jednej bazie SQLite (`brain.db`), ścisłych bramkach pre-commit oraz pętli uczenia się, który trwale eliminuje duplikację, fałszywe sukcesy i brak testów.

---

## 1. Mapa Decyzji (Wayfinder)

Poniższa mapa definiuje kluczowe decyzje architektoniczne i kierunek migracji workspace'u:

- **D-01: Jedna baza `brain.db`** (Zastąpienie rozproszonych plików i baz scentralizowaną bazą SQLite z obsługą FTS5 dla lekcji, decyzji, sesji i problemów).
- **D-02: Wymuszenie bramek i testów** (Automatyczne sprawdzanie spójności przez `check_workspace_integrity.py` oraz hooki pre-commit blokujące naruszenia kodu i białych znaków).
- **D-03: Zamknięcie sesji i handoff** (Rygorystyczny kontrakt flag `handoff/flags/` z automatyczną generacją `HANDOFF.md` i walidacją `--check`).
- **D-04: Separacja fabryki od produktu** (Strukturalny podział na niezmienne zasoby referencyjne/szablony oraz dynamiczne artefakty robocze i wyniki runów).
- **D-05: Utrwalanie diagnoz (Active Recall)** (Przechwytywanie problemów w `brain/problems/` oraz obowiązkowe przeszukiwanie indeksu pamięci przed rozpoczęciem modyfikacji).

---

## 2. Rejestr Decyzji Architektonicznych (ADR)

- **[ADR-001: Jedna centralna baza SQLite `brain.db`](brain/decisions/ADR-001-single-brain-db.md)**: Scentralizowanie wiedzy operacyjnej, lekcji, problemów i historii w jednym pliku SQLite z FTS5 zamiast rozproszonych plików `.md` i niezależnych baz.
- **[ADR-002: Automatyczne bramki i testy obowiązkowe](brain/decisions/ADR-002-enforcing-gates-and-tests.md)**: Wprowadzenie rygorystycznych skryptów weryfikacji integralności oraz hooków pre-commit uniemożliwiających zatwierdzenie kodu niespełniającego kryteriów testowych.

---

## 3. Lista Zadań i Harmonogram (Unlazy Decomposition)

Zadania podzielone są na etapy po maksymalnie 90 minut, z jasnymi kryteriami akceptacji i zależnościami (szczegóły w [TASKS.md](TASKS.md)):

- **Etap 01: Fundamenty i Baza Wiedzy**
  - `T101`: Stworzenie uniwersalnej bazy SQLite `brain/brain.db` ze schematem FTS5 (szac. 60 min, dep: brak).
  - `T102`: Konfiguracja schematu L0–L4 ICM i struktury katalogów (szac. 45 min, dep: T101).
- **Etap 02: Bramki Egzekwujące i Automatyzacja**
  - `T201`: Implementacja skryptu `check_workspace_integrity.py` (szac. 90 min, dep: T102).
  - `T202`: Konfiguracja hooka pre-commit i walidacji CRLF/BOM/sekretów (szac. 60 min, dep: T201).
- **Etap 03: Pętla Uczenia i Zamknięcie Sesji**
  - `T203`: Skrypt automatycznego generowania i walidacji flag handoff `build_handoff.py` (szac. 60 min, dep: T102).
  - `T204`: Mechanizm Active Recall i rejestr problemów `problems/` (szac. 90 min, dep: T101, T202).
- **Etap 04: Migracja Narzędzi i Testy**
  - `T401`: Migracja sprawdzonych skryptów pomocniczych do `tools/` z testami jednostkowymi (szac. 90 min, dep: T102).
  - `T402`: Przegląd ostateczny i Walk Test nowego workspace'u (szac. 60 min, dep: T202, T203, T204, T401).

---

## 4. Architektura i Hierarchia Kontekstu (ICM-Architect)

Workspace zorganizowany jest zgodnie z 5-warstwową hierarchią kontekstu (L0–L4) oraz rygorystycznym podziałem na fabrykę i produkt.

### Drzewo katalogów docelowych:
```text
workspace/
  AGENTS.md                  # L0: Tożsamość workspace'u i główny router
  CLAUDE.md                  # L0: Katalog główny i reguły routingu
  CONTEXT-MAP.md             # L1: Mapa portfela i bounded contexts
  TASKS.md                   # Rejestr zadań unlazy
  PLAN.md                    # Dokument planowania przebudowy
  scripts/                   # Skrypty systemowe, bramki i testy weryfikacji
  brain/                     # Baza wiedzy i pamięć systemowa
    brain.db                 # Centralna baza SQLite (lekcje, decyzje, sesje, problemy)
    problems/                # Rejestr wykrytych problemów i błędów
    decisions/               # ADR-y (Architecture Decision Records)
  tools/                     # Narzędzia operacyjne z wbudowanym selftest (Python stdlib)
  logs/                      # Logi systemowe i artefakty runów
  handoff/                   # Handoff state i pliki flag (1 plik = 1 właściciel)
    flags/                   # Flagi sesyjne
  projects/                  # Portfel projektów badawczych i rozwojowych
    _archive/                # Archiwum wygasłych zasobów (grade: demoted)
```

### Opis warstw kontekstu (L0–L4):
- **L0 (`AGENTS.md`)**: Stała tożsamość agenta, zasady token efficiency, reguły bezpieczeństwa i odsyłacze do warstwy wyższej.
- **L1 (`CONTEXT.md`)**: Katalog główny workspace'u, routing zadań, mapowanie projektów i modułów.
- **L2 (`projects/*/CONTEXT.md`, `wayfinder/`)**: Kontrakty i pliki planowania projektów.
- **L3 (`brain/decisions/`, `tools/`)**: Stabilne reguły, ADR-y, narzędzia fabryczne i zasoby wielokrotnego użytku.
- **L4 (`handoff/flags/`, `logs/`, `brain/problems/`)**: Dynamiczne artefakty powiązane z bieżącym runem i stanem sesji.

---

## 5. Mechanizmy Zapobiegawcze

Aby powtarzające się problemy (duplikacja, fałszywe sukcesy, puste sesje) nie powróciły, workspace wdroży następujące mechanizmy:
1. **Bramki integralności przed commitem (`check_workspace_integrity.py` + hook pre-commit)**: Każda próba commita przechodzi automatyczną weryfikację stanu handoff, spójności strukturalnej i braku kolizji case-folded.
2. **Zakaz pustych sukcesów (Zasada Dowodu)**: Żaden agent nie może oznaczyć zadania jako wykonane bez jednoznacznego dowodu (`tool_result`, `git diff`, `git log` lub wynik testu).
3. **Pętla Active Recall**: Obowiązkowe odpytanie indeksu pamięci i rejestru `brain/problems/` przed modyfikacją kodu, uniemożliwiające powtarzanie znanych błędów.
4. **Jedno źródło prawdy (`brain.db` + flagi handoff)**: Unikanie rozproszonych plików stanu; każdy stan ma jednoznacznego właściciela i ścisły schemat walidacji.

---

## 6. Kryteria Sukcesu

Przebudowę workspace'u uznamy za w pełni zakończoną i skuteczną, gdy spełnione zostaną następujące kryteria:
- **Zero pustych sesji**: Każda zakończona sesja pozostawia poprawnie zweryfikowaną flagę handoff oraz wpis w rejestrze.
- **100% zielonych bramek**: Skrypt `check_workspace_integrity.py` oraz testy w `scripts/` przechodzą bezbłędnie (exit 0).
- **Brak duplikacji wiedzy**: Wszystkie decyzje mają swoje jednoznaczne ADR-y w `brain/decisions/`, a baza `brain.db` integruje zapytania FTS5.
- **Przechodzenie Walk Testu**: Nowy agent bez wcześniejszego kontekstu potrafi przejść ścieżkę od `AGENTS.md` do wykonania zadania i zamknięcia sesji w czasie poniżej 10 minut.
