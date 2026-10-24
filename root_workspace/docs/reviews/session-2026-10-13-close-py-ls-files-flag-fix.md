# close.py --error-unmatch fix — retrospektywa (2026-10-13)

## Kontekst
Sesja 2 (`state-export-levels`) usunęła `repomix.config.json` z roota. `close.py` próbował zweryfikować `--include repomix.config.json`, ale `check_includes` używał `git ls-files --error-match`, co zwracało `error: unknown option`. Wynik: `close.py` blokował się na usuniętym pliku, mimo że plik był w historii git.

## Fix (już w commicie `abc78c4a72e97ce5b10f142e0aeca974083fc1d0`)
Zamieniono `--error-match` na `--error-unmatch` w 2 miejscach (`check_includes`, `dry_run`).

## Rozdzielenie
Zmiana weszła w commit `state-export-levels` bez własnej flagi. Ta flaga + raport rozdzielają ją retrospektywnie. Kod bez zmian.

## not checked:
- audyt innych skryptów pod kątem `--error-match` (nie wykonany)

## Tool calls
| Wartość | Komenda | Surowy output (fragment) |
|---------|---------|--------------------------|
| `abc78c4a72e97ce5b10f142e0aeca974083fc1d0` | `git log --all --oneline -- scripts/close.py` | `abc78c4a72 state-export-levels: state-export-levels` |
| `2` | `git show abc78c4a72e97ce5b10f142e0aeca974083fc1d0 -- scripts/close.py` | `is_tracked = subprocess.run(["git", "ls-files", "--error-unmatch", i], ...)` |
