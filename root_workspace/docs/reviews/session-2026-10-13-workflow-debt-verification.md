# Weryfikacja sesji workflow-debt-closure (2026-10-13)

## Cel

Weryfikacja pięciu twierdzeń z raportu `workflow-debt-closure` + domknięcie T10 i cutoff.

## Tabela weryfikacji

| Twierdzenie | Status | Tool call |
|-------------|--------|-----------|
| walk test passes, 2 ready | POTWIERDZONE | `read CLAUDE.md` (linie 1-40) + `read docs/workflow/README.md` (linie 1-30) — oba outputy wklejone niżej |
| R16 advisory wygasa po 30 min | POTWIERDZONE | `read scripts/check_workspace_integrity.py` (funkcja R16) + żywy `check_workspace_integrity.py` — okno 1800 s w kodzie, R16 fireuje teraz dla commita z tej doby |
| cutoff 2026-10-14 | OBALONE (decyzja: 2026-10-13) | `read scripts/pre_close_check.py` (krok 11) + test `--enforce-after` na raporcie z datą z tej doby bez `## Tool calls` → FAIL; stara wartość dawała SKIPPED |
| T10 rozstrzygnięte | OBALONE | `read docs/wayfinder-retrieval-map.md` — wiersz T10 był `open` mimo rozstrzygnięcia R19 w Decisions; zmieniono na `closed` |
| `_tmp_*` w `not checked:` | OBALONE (częściowo) | `grep _tmp_` w `handoff/flags/` — flaga wymienia tylko liczebnik 9 plików bez nazw; pełna lista dopisana do `not checked:` tego raportu |

## Domknięcia

- T10: `closed` — R19 rozstrzygnięta w poprzedniej sesji (długiem był sam untracked plik, usunięty za zgodą właściciela, bez zmian w bramce), więc wiersz nie miał podstaw do `open`.
- cutoff: `2026-10-13` (Opcja B) — docstring `verify_report_evidence.py` mówi, że standard `## Tool calls` wprowadzono w dacie z tej doby; cutoff o dobę późniejszy oznaczałby zero egzekwowania w dniu wprowadzenia (dowód: ten sam raport testowy daje SKIPPED przy starej wartości, FAIL przy nowej).
- walk test: potwierdzony dwoma readami niżej; odpowiedź: `scan_secrets` uruchamia się przez `python scripts/scan_secrets.py --staged` (lub z listą plików).
- T17: dopisane do mapy (`open`) — R16 fireuje dla zmian w `scripts/**` także gdy nie było nieznanego błędu ani drugiej porażki (obie sesje workflow tak oberwały); kod nie zna warunku "czy było co debugować". Bez zmian w `check_workspace_integrity.py` w tej sesji.

## Walk test (dwa ready)

Read 1: `read CLAUDE.md` (linie 1-40) — wiersz routingu:

```
| `docs/workflow/README.md` | Reference | Enforcement mechanisms: scan_secrets, pre_close_check, verify_report_evidence (contract: `docs/workflow/CONTEXT.md`) |
```

Read 2: `read docs/workflow/README.md` (linie 1-30) — odpowiedź na pytanie gdzie uruchamiam `scan_secrets`:

```
- `scripts/scan_secrets.py` — wykrywa `sk-ant-`, `sk-proj-`, `ghp_/gho_/ghs_`,
  `thk_live_`, `AQ.` (30+ znaków), `Bearer`, PEM. Uruchomienie:
  `python scripts/scan_secrets.py --staged` (lub lista plików).
  Output `file:line [pattern]` — nigdy wartości. Exit 1 = blokada.
```

Wniosek: po 2 readach wiadomo, że folder `docs/workflow/` istnieje, dokumentuje `scan_secrets.py` i że uruchamia się go komendą z linii powyżej. Walk test przechodzi bez poprawek struktury.

## Dowody R16

Fragment `check_r16_session_memory_usage` (linie 750-810, warunek okna):

```
if time.time() - commit_epoch > 1800:
    return  # the matching commit is older than the window: out of scope
```

Żywy output `python scripts/check_workspace_integrity.py` z tej sesji:

```
- R16 session-memory usage: the latest commit touching scripts/**/hooks/**/skills/**/.dsh/** (last 30 min) left no fresh queries.jsonl trace and no mention of `query` in its subject — the door (debug-with-memory) was not visited
OK: workspace root holds 28 declared entries, 6 projects, all routing links resolve
```

R19 milczy (brak linii R19 w outputcie). HEAD to commit sesji `workflow-debt-closure` (hash w backtickach w tabeli).

## Dowód cutoff (krok 11)

Raport testowy z datą z tej doby bez sekcji `## Tool calls`, zawierający liczbę 0.376:

```
CLAIMED_NUMBERS=2 TOOLCALL_ROWS=0 HAS_TOOLCALLS_SECTION=False
MISSING_TOOLCALLS_SECTION: raport nie ma sekcji ## Tool calls
MISSING: 0.376
exit=1
```

Ten sam plik przy starej wartości cutoff:

```
SKIPPED_PRE_STANDARD: raport z 2026-10-13 sprzed 2026-10-14, sekcja ## Tool calls nie wymagana
exit=0
```

## Tool calls

| Wartość | Komenda | Surowy output (fragment) |
|---------|---------|--------------------------|
| `workflow-debt-closure-2026-10-13` | `read handoff/flags/workflow-debt-closure-2026-10-13.md` | `R19 naprawione, R16 rozstrzygnięte, verify_report_evidence podłączone` |
| T10 open→closed | `read docs/wayfinder-retrieval-map.md` | `Rozstrzygnij R19 — retired flagi nie wyciszył bramki` |
| `--enforce-after 2026-10-13` | `read scripts/pre_close_check.py` (krok 11) | `--enforce-after", "2026-10-13", r` |
| SKIPPED_PRE_STANDARD | `read scripts/verify_report_evidence.py` | `skip reports with a filename date older than this` |
| 750-810 (linie R16) | `read scripts/check_workspace_integrity.py` | `if time.time() - commit_epoch > 1800` |
| 1800 | `read scripts/check_workspace_integrity.py` | `if time.time() - commit_epoch > 1800` |
| R16 fires teraz | `python scripts/check_workspace_integrity.py` | `left no fresh queries.jsonl trace and no mention of query in its subject` |
| routing docs/workflow | `read CLAUDE.md` (linie 1-40) | `docs/workflow/README.md \| Reference \| Enforcement mechanisms` |
| `python scripts/scan_secrets.py --staged` | `read docs/workflow/README.md` (linie 1-30) | `Uruchomienie: python scripts/scan_secrets.py --staged` |
| 0.376 | `python scripts/verify_report_evidence.py --enforce-after 2026-10-13 <raport-bez-sekcji>` | `MISSING: 0.376 / exit=1` |
| `646be52` | `git log --oneline -5` | `workflow-debt-closure-2026-10-13` na HEAD |
| 9 plików `_tmp_*` bez nazw | `grep _tmp_ handoff/flags/` | `not checked: _tmp_* z eval/ (9 plików, dług przejęty z poprzedniej sesji)` |

## not checked:

- `_tmp_ask_by_graphrag.json`, `_tmp_frozen_golds.json`, `_tmp_run_ask_benchmark.py`, `_tmp_run_graphrag_on_trust.py`, `_tmp_run_v2_comparison.py`, `_tmp_trust_by_ask.json`, `_tmp_v2_comparison.json`, `_tmp_v2_match_table.json`, `_tmp_v2_questions.json` — 9 plików roboczych z eval/ (dług przejęty; flaga poprzedniej sesji podała tylko liczebnik).
- Untracked `docs/reviews/session-2026-10-13-*.md` i `handoff/flags/ask-user-question-fixed.md` (cudze, nie ruszane).
- Wszystko, czego ten raport nie cytuje z tool calla.

## R18 / governance

Ta sesja jest porządkowo-weryfikacyjna. Governance streak — sprawdź `check_workspace_integrity.py` (output wklejony wyżej; R19 milczy, R16 to advisory z oknem 30 min).
