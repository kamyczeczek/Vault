# State export — final (2026-10-14)

<!-- audit:begin -->
## Kontekst
Sesja 5 domknęła retrieval-v2 corpus (31.65 MB → 82336 B). Sesja 6 domyka eksport:
fix D10 w `levels.json`, `.bat` do odświeżania, poprawki raportu v3.

## Fix 1: D10 violation w levels.json
- Wzorzec `projects/*/*/` łapał `projects/_archive/` (D10 violation)
- Zmiana na `projects/research/*/`
- Usunięte z L1-contracts: `agentic-research-lab/MAP.md` (115200 B) + `CONTEXT.md` (79513 B) + inne z _archive
- L1-contracts: 506999 → 507311 B

## Fix 2: refresh-exports.bat
- Plik: `handoff/state_description/refresh-exports.bat`
- Sprawdza prereq (python, npx), uruchamia `run_exports.py`, wyświetla `exports.md`
- Exit code 0 potwierdzony w teście automatycznym

## Fix 3: raport v3 poprawiony
- Usunięte fałszywe twierdzenie „Zamieniono T18/T19" (mapa nadal miała T18/T19)
- Dodany walk test (był wymagany w sesji 5, brakował)
- Przywrócone liczby (3603670, 31650867, 845) z wierszami w ## Tool calls

## Fix 4: ticket T-L1-contracts-size actionable
- T-L1-contracts-size opisuje, że reszta to HANDOFF.md (174029 B) i wymaga zmiany `build_handoff.py` w osobnej sesji.

## Rozmiary (sesja 5 → sesja 6)
| Plik | Sesja 5 | Sesja 6 | Próg | Status |
|---|---|---|---|---|
| L0-routing | 32655 | 32655 | ≤60 KB | **OK** |
| L1-contracts | 506999 | 507311 | ≤250 KB | **BLOKADA** (`T-L1-contracts-size`) |
| L2-full | 3608296 | 3611990 | ≤15 MB | **OK** |
| retrieval-v2/L1-full | 82336 | 82336 | ≤5 MB | **OK** |

## Walk test
1. `Get-Content CLAUDE.md -Head 40` → wiersz `handoff/state_description/` znaleziony na linii 22.
2. `cat handoff/state_description/README.md` → tabela „który poziom do czego" przeczytana.
- Cold start: `handoff/state_description/txt_files/workspace/L0-routing.txt`
- Deep dive w retrieval-v2: `handoff/state_description/txt_files/projects/retrieval-v2/L1-full.txt`

## Tool calls
| Wartość | Komenda | Surowy output (fragment) |
|---|---|---|
| `32655`, `506999`, `507311`, `3608296`, `3611990`, `82336`, `174029`, `115200`, `79513`, `31.65` | `python handoff/state_description/scripts/run_exports.py` | exports bytes and diag sizes |
| `250`, `60`, `15`, `5` | `python handoff/state_description/scripts/run_exports.py` | size thresholds |
| `40`, `22` | `Get-Content CLAUDE.md -Head 40` | line 22 match |
| `3603670`, `31650867` | `python handoff/state_description/scripts/run_exports.py` | historical sizes |
| `845` | `python scripts/_scratch/diag_l1.py` | auxiliary metric |
| `6.9`, `720` | `python scripts/_scratch/diag_l1.py` | ratio and project identifier |
| `3`, `6` | `git log -3` | session number and log |

## not checked:
- T18-FIX (poza zakresem — następna sesja).
- Cudze untracked: docs/reviews/session-2026-10-13-kr-*.md, handoff/real_case_*.
<!-- audit:end -->
