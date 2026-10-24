# TASKS.md — Przebudowa Workspace'u (Unlazy Decomposition)

Zadania podzielone są na niezależne etapy (fazy). Każde zadanie szacowane jest na maksymalnie 90 minut, ma zdefiniowane kryteria akceptacji (test lub bramka) oraz jednoznaczne zależności (`blockedBy`).

---

## Etap 01: Fundamenty i Baza Wiedzy (Core & Brain)

### [x] T101: Stworzenie uniwersalnej bazy SQLite `brain/brain.db` ze schematem FTS5
- **Cel:** Zastąpienie rozproszonych plików i baz jedną instancją SQLite z obsługą full-text search (FTS5) dla lekcji, decyzji, sesji i problemów.
- **Szacowany czas:** 60 min.
- **Kryteria akceptacji / Test:** Skrypt inicjalizujący tworzy tabele `lessons`, `decisions`, `sessions`, `problems` z indeksem FTS5; selftest przechodzi pomyślnie (`python scripts/test_brain_db.py`).
- `blockedBy:` []

### [x] T102: Konfiguracja i walidacja struktury L0–L4 ICM
- **Cel:** Ustanowienie brakującego elementu strukturalnego `brain/problems/` oraz skryptu weryfikacji struktury ICM/workspace (`scripts/test_workspace_structure.py`). (Uwaga: katalogi `handoff/`, `projects/_archive/` i `tools/` istnieją zgodnie z konwencją workspace; `stages/` i root `tests/` zastąpione odpowiednio przez `projects/` / `wayfinder/` i `scripts/`).
- **Szacowany czas:** 45 min.
- **Kryteria akceptacji / Test:** Skrypt `python scripts/test_workspace_structure.py` potwierdza obecność wymaganych struktur ICM L0–L4 (`AGENTS.md`, `CLAUDE.md`, `brain/`, `brain/problems/`, `tools/`, `handoff/`, `projects/_archive/`).
- `blockedBy:` [T101]

---

## Etap 02: Bramki Egzekwujące i Automatyzacja (Gates & Hooks)

### [x] T201: Implementacja skryptu `check_workspace_integrity.py`
- **Cel:** Stworzenie wszechstronnego skryptu sprawdzającego spójność workspace’u (bramki Q0/Q1, stan handoff, brak kolizji case-folded).
- **Szacowany czas:** 90 min.
- **Kryteria akceptacji / Test:** Uruchomienie `python scripts/check_workspace_integrity.py` zwraca kod exit 0 na czystym stanie i exit 1 przy naruszeniu reguł (zweryfikowane: 2026-10-14, output w logu: exit 0).
- `blockedBy:` [T102]

### [x] T202: Konfiguracja hooka pre-commit i walidacji CRLF/BOM/sekretów
- **Cel:** Podpięcie skryptu weryfikacji pod git pre-commit hook w celu blokowania niedozwolonych commitów oraz skanowania sekretów i białych znaków.
- **Szacowany czas:** 60 min.
- **Kryteria akceptacji / Test:** Próba commita z błędnym formatem białych znaków (`git diff --check`) lub naruszeniem bramek kończy się przerwaniem commita z czytelnym komunikatem (zweryfikowane: 2026-10-14, output w logu: hook podpięty i zawiera git diff --cached --check).
- `blockedBy:` [T201]

---

## Etap 03: Pętla Uczenia i Zamknięcie Sesji (Ralph-Loop & Session Closure)

### [x] T203: Skrypt automatycznego generowania i walidacji flag handoff (`build_handoff.py`)
- **Cel:** Utrzymanie kontraktu „jedna flaga = jeden plik = jeden właściciel” z rygorystycznym trybem `--check` zapobiegającym przeterminowaniu stanu.
- **Szacowany czas:** 60 min.
- **Kryteria akceptacji / Test:** `python scripts/build_handoff.py --check` weryfikuje aktualność `HANDOFF.md` i failuje w przypadku niezgodności (zweryfikowane: 2026-10-14, output w logu: exit 0).
- `blockedBy:` [T102]

### [x] T204: Mechanizm Active Recall i rejestr problemów (`problems/`)
- **Cel:** Wymuszenie odpytania pamięci sesyjnej przed rozpoczęciem modyfikacji kodu oraz rejestrowanie napotkanych problemów w strukturze `brain/problems/`.
- **Szacowany czas:** 90 min.
- **Kryteria akceptacji / Test:** Próba zapisu pliku bez uprzedniego sprawdzenia indeksu pamięci lub braku wpisu w rejestrze problemów blokowana jest przez guardrail (zweryfikowane: 2026-10-14, output w logu: test_active_recall.py przechodzi pomyślnie).
- `blockedBy:` [T101, T202]

---

## Etap 04: Migracja Narzędzi i Testy (Tools & Verification)

### [x] T401: Migracja sprawdzonych skryptów pomocniczych do `tools/` z testami jednostkowymi
- **Cel:** Przeniesienie skryptów operacyjnych do spójnego katalogu `tools/` i opatrzenie ich hermetycznymi testami ststdlib (każde narzędzie z `--selftest`).
- **Szacowany czas:** 90 min.
- **Kryteria akceptacji / Test:** Narzędzia w `tools/` przechodzą testy `--selftest` bez zewnętrznych zależności poza Python stdlib (zweryfikowane: 2026-10-14, output w logu: wszystkie narzędzia w tools/ przechodzą --selftest).
- `blockedBy:` [T102]

### [~] T402: Przegląd ostateczny i Walk Test nowego workspace'u
- **Cel:** Przeprowadzenie zimnego przejścia (walk test) przez nowego agenta zgodnie z metodyką ICM, bez znajomości historii.
- **Szacowany czas:** 60 min.
- **Kryteria akceptacji / Test:** Agent bez kontekstu historycznego potrafi zlokalizować cel, sprawdzić stan bazy, uruchomić testy i poprawnie zamknąć sesję flagą. (Status: PARTIAL — zakończony z 3 findings w `handoff/flags/T402-walk-test-2026-10-14.md`).
- `blockedBy:` [T202, T203, T204, T401]

### [~] T402-walk-test: Walk Test świeżego agenta
- **Cel:** Przeprowadzenie walk testu przez nowego agenta bez znajomości historii.
- **Szacowany czas:** 60 min.
- **Kryteria akceptacji / Test:** Świeży agent (bez historii) w <10 min przechodzi od AGENTS.md do zamknięcia sesji flagą; output: transkrypt sesji. (Status: PARTIAL — 5 min, werdykt PARTIAL, 3 findings).
- `blockedBy:` []
