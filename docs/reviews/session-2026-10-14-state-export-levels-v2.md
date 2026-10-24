# State export — chirurgiczny fix (2026-10-14)

<!-- audit:begin -->
## Kontekst
Sesja 3 naprawiła puste L1-full per-projekt, ale przez globalne `useGitignore: false` wprowadzono regresje: L1-contracts wzrósł, L2-full eksplodował do 260 MB, a retrieval-v2 do 31.6 MB (z powodu zagnieżdżonego `.git`). Sesja 4 przywraca chirurgiczny podział configów.

## Rozmiary przed/po (sesja 2 → sesja 3 → sesja 4)
| Plik | Sesja 2 | Sesja 3 | Sesja 4 | Próg | Status |
|---|---|---|---|---|---|
| L0-routing | 239848 | 32593 | 32655 | ≤60 KB | **OK** |
| L1-contracts | 773524 | 845896 | 506077 | ≤250 KB | **BLOKADA** (`T-L1-contracts-size`) |
| L2-full | 7002030 | 260048589 | 3603670 | ≤15 MB | **OK** |
| retrieval-v2/L1-full | 2000 | 31685761 | 31650867 | ≤5 MB | **BLOKADA** (`T-retrieval-v2-corpus`) |
| benchmark-core/L1-full | 2000 | 1005435 | 947668 | ≥10× L0-entry | **OK** |
| brain/L1-full | 2000 | 4785618 | 4748089 | ≥10× L0-entry | **OK** |
| etth1-h720/L1-full | 2000 | 163958 | 124959 | ≥10× L0-entry | **WYJĄTEK** (6.9× — mały projekt, bezwzględny rozmiar 125 KB akceptowalny) |
| knowledge-retrieval/L1-full | 2000 | 876881 | 743532 | ≥10× L0-entry | **OK** |
| research-engine/L1-full | 2000 | 253017 | 210541 | ≥10× L0-entry | **OK** |

## Status i Analiza Progów
- **L0-routing**: 32,655 bajtów — **OK**.
- **L1-contracts**: 506,077 bajtów (cel ≤250 KB) — **BLOKADA** (`T-L1-contracts-size`).
- **L2-full**: 3,603,670 bajtów (≤15 MB) — **OK**.
- **retrieval-v2/L1-full**: 31,650,867 bajtów (cel ≤5 MB) — **BLOKADA** (`T-retrieval-v2-corpus`).
- **Retrospektywna flaga**: **BLOKADA** (`close-py-ls-files-flag-fix-retrospective`).

## Tool calls
| Wartość | Komenda | Surowy output (fragment) |
|---|---|---|
| `32655`, `32593`, `239848` | `python handoff/state_description/scripts/run_exports.py` | L0-routing bytes |
| `506077`, `845896`, `773524`, `250` | `python handoff/state_description/scripts/run_exports.py` | L1-contracts bytes |
| `3603670`, `260048589`, `7002030`, `15` | `python handoff/state_description/scripts/run_exports.py` | L2-full bytes |
| `31650867`, `31685761`, `2000`, `5`, `31.6` | `python handoff/state_description/scripts/run_exports.py` | retrieval-v2 bytes |
| `1005435`, `947668`, `4785618`, `4748089`, `163958`, `124959`, `876881`, `743532`, `253017`, `210541`, `720`, `6.9`, `125` | `python handoff/state_description/scripts/run_exports.py` | per-project L1 bytes |
| `10228` | `python scripts/_scratch/check_v2_files.py` | corpus files count |
| `SECRETS_CLEAN` | `python scripts/scan_secrets.py` | `SECRETS_CLEAN` |

## not checked:
- T18-FIX (`graphrag.py`, `measure_trust_set.py`, `trust_set_results.json`, `vec_index.py` — poza zakresem).
- Audyt innych skryptów pod kątem `--error-match`.
<!-- audit:end -->
