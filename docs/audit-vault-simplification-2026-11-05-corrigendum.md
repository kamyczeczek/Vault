# Poprawiona ocena i plan upraszczania repo

**Krótko: dzięki za rzetelną krytykę. Poprawiam błędy i upraszczam do 3 konkretnych commitów.**

## Poprawione liczby (z audytu)

| Element | Byłem | Poprawne |
|---|---|---|
| `projects/research/` | 594 MB, 594 pliki | **37,88 MB, 594 pliki** |
| `kb/` (tracked) | 361 MB | **22,39 MB** (na dysku 361 MB nieśledzonych pluginów) |
| Całkowity tracked | 648 MB | **~350 MB** (po odjęciu duplikatowego backupu 291,54 MB) |
| Archiwum backup | 291,54 MB, 3152 pliki | **DUPLIKATE** – ten sam zbiór co `projects/_archive/` |

## Najważniejszy błąd (bezpieczeństwo)

Planowałem: *"żywy klucz w historii"*. **To nieprawda.** `scripts/scan_secrets.py` → **`SECRETS_CLEAN`**. Wzorzec `sk-nry` trafił tylko na maskowaną wartość `sk-nr...50` w `state.json` archiwu oraz na wzorce w samym scannerze. Nie znaleziono aktywnego klucza. Poprawna kolejność: **najpierw pełny skan, potem ewentualna rotacja** — a nie od razu teza o wycieku.

## Trzy commit zamiast dziesięciu ticketów

Po analizie krytyki i własnych liczb, plan uproszczam do trzech niezależnych commitów, które można wykonać w tej samej sesji:

### C1: Usuń duplikatowe backupy z Git (najważniejsze)
```
git rm -r projects/_archive.backup-20261104/
# Dodaj do .gitignore wzorzec na przyszłość (już jest, ale warto potwierdzić):
**/.env**
**/.env.*
# Commit z wiadomością: "Remove duplicate archive backup (291 MB), consolidate with _archive/"
```
**Weryfikacja:** `git status` — ścieżka usunięta; `python scripts/check_workspace_integrity.py` — OK (nie używa tych plików).

### C2: Weryfikacja sekretów + rotacja jeśli konieczna
```
# 1. Pełny skan (już był: SECRETS_CLEAN)
# 2. Jeśli chcesz bezpiecznika: rotacja OPENAI_API_KEY i dodanie nowej wartości do DECISIONS.md
# 3. Potwierdź: grep -rl "sk-nry" . --exclude-dir=.git | grep -v ".env.example" | wc -l
#    Wynik powinien być 0 lub tylko w .env.example (which jest na liście wykluczeń).
```
**Weryfikacja:** `scripts/scan_secrets.py` nadal `SECRETS_CLEAN`. Jeśli po rotacji — dodaj wpis w `DECISIONS.md`, nie zostawiaj kluczy w historii.

### C3: Scel `AGENTS.md` + `CLAUDE.md` + napraw `etth1-h720`
```
# Scel pliki wejściowe do jednego AGENTS.md (patrz "Target Minimal Architecture" w poprzednim dokumencie, ale krócej):
# - Usuń lub uprość CLAUDE.md na korzyść AGENTS.md (zgodne z inwariantem ICM #2)
# - W README etth1-h720: dodaj znak zamknięcia obok projektu (S49 CLOSED REJECT)
# - Zaktualizuj AGENTS.md tak, by kierował tylko do research/active/
# Commit: "Consolidate entry files; mark etth1-h720 closed; AGENTS.md sole router"
```
**Weryfikacja:** Nowy `AGENTS.md` ma ≤60 linii (liczba linii); `grep -r "where am I" . --include="AGENTS.md"` wskazuje na jedno miejsce; `etth1-h720` ma adnotację o बंद S49.

## Dlaczego to lepsze

- **Liczby są prawdziwe** – nie wymyślone na górze.
- **Bezpieczeństwo**: zamiast krzyczeć o wycieku, wykonuję weryfikację i ewentualną rotację na pewnych fundamentach.
- **Prawdziwa redukcja**: usuwam 291 MB z Git, a nie przepisuję listy TODO.
- **Skrypty**: nie przetną po sztucznej liczbie 20, tylko zachowuję to, co jest potrzebne do gate'ów (`check_workspace_integrity`, `build_handoff`, `build_state`) – resztę ewentualnie w kolejnym kroku.
- **Brak warstwy procesu**: trzy commity, a nie dziesięć ticketów na sesję. Można to zrobić w jednym dziale.

## Co dalej (po tych trzech commitach)

Jeśli po C1–C3 chcesz further reductions:
- Przeanalizować, który z 113 plików `scripts/*.py` jest martwy (brak referrerów w `GATES.md`/`STATE.md`), a nie corte po liczbie.
- Scalić resztę `CONTEXT.md` z 124 do ≤30 (automatycznie po usunięciu backupu i projektów archive/archive.backup).
- Ewentualnie wayfinder na prawdziwym trackerze, jeśli potrzebna dłuższa praca wymiarowa.

**Flaga zakończenia:** Po tych trzech commitach napiszę flagę `handoff/flags/vault-simplification-done-2026-11-05.md` i zaktualizuję `STATE.md`/`STATUS.md` – tak, jak zrobiłem wcześniej przy auditzie, bez dorzucania nowego długu.
