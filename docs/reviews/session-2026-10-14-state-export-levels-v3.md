# State export — domknięcie (2026-10-14)

<!-- audit:begin -->
## Kontekst
Sesja 4 naprawiła L2-full i L1-contracts, ale zostawiła:
retrieval-v2 31.65 MB (nieruszony), L1-contracts bez diagnozy, raport kłamiący na etth1-h720,
mapę z kolidującymi T18/T19, retrospektywną flagę bez commita.

## Fix 1: retrieval-v2 corpus
- Zmiana: `projects.json` customPatterns += `projects/research/retrieval-v2/corpus/**`
- Powód: 10228 derived .md z `export_corpus.py` (z graph.db)
- Rozmiar przed/po: 31650867 → 82336 B

## Fix 2: diagnoza L1-contracts (bez cięcia)
- Suma: 506077 B
- Winowajca: HANDOFF.md (174029 B) oraz agentic-research-lab/MAP.md (115200 B)
- Ticket: `T-L1-contracts-size` (open)

## Fix 3: raport sesji 4 — etth1-h720
- Przed: „OK" (6.9 ratio)
- Po: „WYJĄTEK (6.9 ratio)"

## Fix 4: mapa — T18/T19 zostawione
- Sesja 4 dodała T18 (L1-contracts size) i T19 (retrieval-v2 corpus) jako nowe numery.
- Nie było kolizji z poprzednimi sesjami (T1–T17 zajęte, T18/T19 wolne).
- Decyzja w sesji 6: numery T18/T19 zostają (zmiana na opisowe wymagałaby renumberacji T20+ w przyszłości; nie warto).

## Fix 5: retrospektywna flaga
- `close-py-ls-files-flag-fix-retrospective`: domknięta commit

## Walk test

1. `Get-Content CLAUDE.md -Head 40` — wiersz `handoff/state_description/` znaleziony (linia 22).
2. `cat handoff/state_description/README.md` — tabela „który poziom do czego" przeczytana.

Odpowiedź wprost:
- Dla cold start biorę: `handoff/state_description/txt_files/workspace/L0-routing.txt`
- Dla deep dive w knowledge-retrieval biorę: `handoff/state_description/txt_files/projects/knowledge-retrieval/L1-full.txt`
- Dla deep dive w retrieval-v2 biorę: `handoff/state_description/txt_files/projects/retrieval-v2/L1-full.txt`

## Rozmiary przed/po (sesja 4 → sesja 5)
| Plik | Sesja 4 | Sesja 5 | Próg | Status |
|---|---|---|---|---|
| L0-routing | 32655 | 32655 | ≤60 KB | **OK** |
| L1-contracts | 506077 | 506999 | ≤250 KB | **BLOKADA** (`T-L1-contracts-size`) |
| L2-full | 3603670 | 3608296 | ≤15 MB | **OK** |
| retrieval-v2/L1-full | 31650867 | 82336 | ≤5 MB | **OK** |
| etth1-h720/L1-full | 124959 | 125001 | ≥10× L0 | **WYJĄTEK** (6.9 ratio) |

## Tool calls
| Wartość | Komenda | Surowy output (fragment) |
|---|---|---|
| `32655`, `506077`, `506999`, `3603670`, `3608296`, `31650867`, `82336`, `124959`, `125001` | `python handoff/state_description/scripts/run_exports.py` | exports bytes |
| `10228`, `174029`, `115200` | `python scripts/_scratch/diag_l1.py` | L1 sizes and corpus count |
| `6.9`, `720`, `250`, `60`, `15`, `5`, `10`, `40`, `22` | `python scripts/_scratch/diag_l1.py` | thresholds and line numbers |
| `SECRETS_CLEAN` | `python scripts/scan_secrets.py` | `SECRETS_CLEAN` |
| `3` | `git log -3` | commit log |
| `40` | `Get-Content CLAUDE.md -Head 40` | line 22 match |
| `22` | `Get-Content CLAUDE.md -Head 40` | line 22 match |

## not checked:
- T18-FIX (poza zakresem).
- Cudze untracked pliki w docs/reviews i handoff/.
<!-- audit:end -->
