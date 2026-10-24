# State export — poziomy (2026-10-13)

<!-- audit:begin -->
## Cel
Folder `handoff/state_description/` obsługujący N eksportów po (target × poziom).

## Struktura
- `configs/base.json` — ignore + security (bez include)
- `configs/levels.json` — 3 poziomy workspace, 2 poziomy projekt
- `scripts/run_exports.py` — driver (npx.cmd na Windows)
- `README.md` — wybór poziomu
- `exports.md` — index (generated)
- `txt_files/_legacy/` — stare płaskie eksporty z sesji 1

## Root cleanup
- usunięty `repomix.config.json` z roota
- usunięty wpis z `ALLOWED_ROOT` w `scripts/check_workspace_integrity.py`

## Uruchomienie
- Uruchomiono pętlę repomix dla 15 eksportów (3 workspace + 12 projektowych).
- Rozmiar `workspace/L2-full.txt`: 7,002,030 bajtów.
- Skan sekretów na L2: `SECRETS_CLEAN`.
- Brak rekurencji: sprawdzone przez grep w `L2-full.txt` (brak self-reference po zaaplikowaniu ignore dla `txt_files/**`).

## Walk test
Dla cold startu biorę `handoff/state_description/txt_files/workspace/L0-routing.txt`.
Dla deep dive w knowledge-retrieval biorę `handoff/state_description/txt_files/projects/knowledge-retrieval/L1-full.txt`.

## Tool calls
| Wartość | Komenda | Surowy output |
|---|---|---|
| 15 | `python handoff/state_description/scripts/run_exports.py` | 15 `[repomix] ->` lines and `Zapisano index: ...exports.md` |
| 7002030 | `cat handoff/state_description/exports.md` | `| handoff\state_description\txt_files\workspace\L2-full.txt | 7,002,030 | L2-full |` |
| 0 | `python scripts/scan_secrets.py handoff/state_description/txt_files/workspace/L2-full.txt` | `SECRETS_CLEAN` |

## not checked:
- Żadne testy T18-FIX ani `graphrag.py` / `measure_trust_set.py` nie były dotykane ani weryfikowane w tej sesji (poza zakresem).
- Pliki tymczasowe `_tmp_*` w `eval/` nie dotczą tej sesji.

## R18 / governance
Sesja: ergonomia eksportu (nie retrieval). T18-FIX nadal otwarte.
<!-- audit:end -->
