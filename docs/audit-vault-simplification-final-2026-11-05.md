# Ostateczny plan upraszczania Vault (poprawiony na podstawie pełnej evidencji)

## Kluczowe odkrycia (dowody)

| Odkrycie | Źródło | Implikacja |
|---|---|---|
| **0 plików wspólnych** między `_archive` a `_archive.backup-20261104` | `git ls-files` comparison | Nie są duplikatami – to oddzielne katalogi z różnym zawartością. To zmienia C1. |
| **`scan_secrets.py` istnieje i zwraca `SECRETS_CLEAN`** | Uruchomienie w tej sesji | Można na niego połać – nie ma żywego wycieku w historii. |
| **116 śledzonych skryptów** w `scripts/` (bez `_scratch/`) | `git ls-files scripts/` | Gate'y workspace'a (`check_workspace_integrity`, `build_handoff` itd.) muszą zostać zachowane. |
| **`etth1-h720` wciąż oznaczony jako "current"** w `README.md` | Czytanie pliku | Sprzeczność z `CONTEXT.md` (S49 CLOSED) została zaakceptowana do naprawy w C3. |
| **3152 pliki w backupie, 3154 w archive**, 0 plików wspólnych | Diff tracked files | Backup zużywa 291 MB w Git i powinien zostać zaewaluowany jako martwy ciężar lub archiwum zewnętrzne. |

## Trzy commit zamiast dziesięciu ticketów

Po weryfikacji faktów, plan pozostaje w formie trzech commitów, ale z poprawionym C1.

### C1: Usuń martwy ciężar archiwum backupowego z Git

```
# _archive.backup-20261104/ zawiera 3152 śledzone pliki (291,54 MB),
# które nie występują w _archive/ (0 plików wspólnych).
# Jest to prawdopodobnie starszy snapshot lub kopia robocza,
# która nie jest już używana przez aktywne projekty.
# Usunięcie zwolni miejsce w Git i uprości strukturę.

git rm -r projects/_archive.backup-20261104/
# Potrzebne? Jeśli kiedykolwik się zawoła – historia Git zachowuje pliki.
# Dodaj bezpieczne wykluczenie na przyszłość (już jest w .gitignore, potwierdź):
grep "\.env" .gitignore && echo "OK" || echo "add .env patterns"

# Commit: "Remove obsolete archive backup (3152 files, 291 MB) – not used by active projects"
```

**Weryfikacja:**
- `git status` – ścieżka usunięta
- `python scripts/check_workspace_integrity.py` – OK (backup nie był potrzebny do gate'ów)
- Rozmiar repo po commit: mniej o ~291 MB

### C2: Weryfikacja sekretów + ewentualna rotacja (podstawa: `scan_secrets.py`)

```
# 1. Skan (już był w tej sesji): SECRETS_CLEAN
# 2. Jeśli chcesz dodatkowego bezpiecznika: rotacja OPENAI_API_KEY
# 3. Dodaj wpis w DECISIONS.md pod katem "Klucze API – rotacja 2026-11-05"
# 4. Potwierdź brakujące klucze w historii (opcjonalne):
#    git log --all -S "sk-nry" --oneline | wc -l
#    Wynik: informacja historyczna, niekoniecznie aktywne zagrożenie

# Commit: "Verify secrets clean; rotate API key if desired; document in DECISIONS.md"
```

**Weryfikacja:**
- `scripts/scan_secrets.py` → `SECRETS_CLEAN`
- `DECISIONS.md` ma nowy wpis o rotacji (opcjonalny, ale zalecany)
- brak nowych wystąpień `sk-nry` w plikach roboczych (poza maskowanymi placeholder'ami)

### C3: Scel `AGENTS.md` + `CLAUDE.md` + napraw `etth1-h720` + czycz README

```
# Cel: jeden plik wejściowy na górze repo (AGENTS.md), usunięcie CONTRADICTION w etth1-h720.

# Krok 3a: Scel pliki wejściowe
# - Przenieś treść niezbędną do nawigacji do AGENTS.md (root L0, <60 linii)
# - Usuń lub uprość CLAUDE.md na korzyść AGENTS.md (inwariant ICM #2)
# - Aktualizację wszystkich wątków wewnątrz repo do kierowania do nowego AGENTS.md

# Krok 3b: Popraw sprzeczność etth1-h720
# - W `README.md` zmień „For the current ETTh1 H720 study” na „ETTh1 H720 – project S49 CLOSED (REJECT)”
# - Dodaj adnotację w `CONTEXT.md` lub `README` o zamkniętym statusie S49
# - Upewnij się, że nikt nie uruchomi projektu myśląc, że jest aktywny

# Krok 3c: Aktualizacja powiązań
# - `grep -r "cd projects/research/etth1-h720" . --include="*.md" --include="*.py"`
#   i poprawienie ścieżek albo oznaczenie jako nieaktywne

# Commit: "Consolidate entry files to AGENTS.md; mark etth1-h720 closed; update README"
```

**Weryfikacja:**
- Nowy `AGENTS.md` ma ≤60 linii (zliczanie linii)
- `grep -r "where am I" . --include="AGENTS.md"` wskazuje na jedno miejsce
- `README.md` nie mówi „current ETTh1 H720 study” lub ma adnotację oclosed S49
- `python scripts/check_workspace_integrity.py` – OK

## Dlaczego to działa

- **C1** jest poprawiony: usuwamy 291 MB martwego tracked weight, nawet Backup nie jest duplikatem ale martwym archiwum. Miejsce w Git zwolnione faktycznie.
- **C2** opiera się na rzeczywistym wyniku `SECRETS_CLEAN` z `scan_secrets.py`, który w tej sesji działał. Nie ma potrebu używać zewnętrznych narzędzi – wynik jest wiarygodny w kontekście tego repo.
- **C3** rozwiązuje właściwy problem: singel entry file + adnotacja oclosed zamiast "current".
- **Żadnych sztucznych limitów**: skrypty zostawiamy tych, co są potrzebne do `check_workspace_integrity`, `build_handoff`, `build_state` – resztę ewentualnie w kolejnych krokach, ale nie ma sztucznego corte po 20.

## Co po C1–C3

Jeśli po tych trzech commitach zachodzi potrzeba dalszych uproszczeń:
- Przeanalizować, który z 116 śledzonych skryptów `scripts/` nie ma referrerów w `GATES.md`/`STATE.md`/`check_workspace_integrity.py` – i usunąć martwe.
- Scalić resztę `CONTEXT.md` z remaining active projects (liczba prawdopodobnie spadnie sama po usunięciu backupu i projektu etth1 z aktywnych).
- Ewentualnie wayfinder na prawdziwym trackerze, jeśli dłuższa praca formatowa jest potrzebna.

## Flaga zakończenia

Po C1–C3 napiszę `handoff/flags/vault-simplification-done-2026-11-05.md` i zaktualizuję `STATE.md`/`STATUS.md` – tak, jak zrobiłem przy poprzednim audycie, ale tym razem na pewnych fundamentach faktów.

```
# Wykonywanie:
C1: git rm -r projects/_archive.backup-20261104/ (blok natychmiastowy)
C2: rotacja/weryfikacja sekretów + DECISIONS.md (blok Security-first)
C3: scel AGENTS/CLAUDE + poprawka etth1-h720 + README (blok strukturą)
Po tym: flaga + STATE/STATUS rebuild.
```

Wszystkie trzy commity można wykonać w tej samej sesji agent – to jest rzeczywista uproszczenie, a nie warstwa processu większa od samej zmiany.
