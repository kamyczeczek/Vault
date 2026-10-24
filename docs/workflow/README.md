# Workflow enforcement — mechanizmy (2026-10-13)

Sesje 8–10 łamały SCARS mimo wpisów. Te mechanizmy je egzekwują.

## Mechanizmy

- `hooks/pre-commit` — whitespace (`git diff --cached --check`), rebuild
  HANDOFF/STATE, integrity gate, **plus skan sekretów** (blokuje commit).
- `scripts/scan_secrets.py` — wykrywa `sk-ant-`, `sk-proj-`, `ghp_/gho_/ghs_`,
  `thk_live_`, `AQ.` (30+ znaków), `Bearer`, PEM. Uruchomienie:
  `python scripts/scan_secrets.py --staged` (lub lista plików).
  Output `file:line [pattern]` — nigdy wartości. Exit 1 = blokada.
- `scripts/pre_close_check.py` — uruchomić **przed** `close.py`. Sprawdza:
  brak flagi, kształt body, `not checked:`, `--include` bez `_scratch`,
  `diff --check`, HANDOFF `--check`, integrity, sekrety. Kończy
  `PRE_CLOSE_READY` / `PRE_CLOSE_BLOCKED`.
- `scripts/verify_report_evidence.py` — uruchomić na raporcie z
  `docs/reviews/`. Wymusza sekcję `## Tool calls`: każda liczba w raporcie
  musi mieć wiersz w tabeli. `ALL_NUMBERS_HAVE_TOOLCALLS` albo lista braków.
- `scripts/check_workspace_integrity.py` — istniejące bramki R1–R20;
  kontrakt w nagłówku pliku, nie powielany tutaj.

## Mapowanie SCARS → mechanizm

```
S59 (raport ≠ tool call)  → verify_report_evidence.py + sekcja ## Tool calls
S60 (close.py ucięty)     → naprawione w close.py (subject + blank + body)
S58 (close.py friction)   → pre_close_check.py
brak (wycieki kluczy)     → scan_secrets.py + hook
```

## Czego NIE ma jeszcze

- Automatyczny triage instrukcji > 3 cele (kandydat: T14).
- Auto-fix stale views (HANDOFF.md, MAP.md) przy pierwszym advisory (T15).
- Weryfikator bramek przepisanych po niepowodzeniu, S62 (T16): wymaga
  porównania CHECK/EXPECT przed/po — na razie tylko ticket.

## Decyzje z sesji workflow-debt-closure-2026-10-13

- **R19** (retired flaga nie wyciszała): bramka działała poprawnie — fireowała
  na untracked `workflow-verification-2026-10-13.md`, a nie na retired-fladze
  (tracked pliki nie są kandydatami). Długiem był sam plik; właściciel
  zgodził się na usunięcie, retired-flaga zostaje jako zapis. Bez zmian w kodzie (S62).
- **R16** (advisory po commicie dotykającym `scripts/**`): sesja enforcement
  nie napotkała nieznanego błędu ani drugiej porażki — drzwi
  `debug-with-memory` nie miały zastosowania, nie było czego zapisywać w
  `queries.jsonl`. R16 to advisory z oknem 30 min, wygasa samo. Bez zmian w kodzie.
- **`verify_report_evidence.py`**: tryb `--enforce-after YYYY-MM-DD` — raporty
  ze starszą datą w nazwie to `SKIPPED_PRE_STANDARD` (retrofit `## Tool calls`
  po fakcie byłby fabrykacją). Wpięte w `pre_close_check.py` (krok 11) dla
  `--include` z `docs/reviews/*.md`, cutoff `2026-10-14`.

## Walk test

Cold agent: otwórz root `CLAUDE.md`, znajdź ten folder w tabeli routingu
(≤2 ready: `CLAUDE.md` → `docs/workflow/CONTEXT.md`). Sprawdź: czy umiesz
odpowiedzieć „gdzie uruchamiam scan_secrets?" bez pytania.
