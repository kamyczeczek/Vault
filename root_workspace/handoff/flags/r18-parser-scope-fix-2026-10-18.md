---
flag: r18-parser-scope-fix-2026-10-18
since: 2026-10-18
owner: mateusz
agent: opencode
model: opencode/glm-5.3-flash-free
origin: session-close
---

`r18-parser-scope-fix-2026-10-18` — 2026-10-18: Naprawa S84a (korekta w S85): R18 parser fałszywie flagował `status: WYKONANE` wpisy, których closing prose zawierała słowo `PENDING_IMPLEMENTATION` (`check_workspace_integrity.py` traktował segment po `re.split(r"(?m)^- id:...")` w całości jako wpis). Fix: helper `_r18_pending_decisions(text, today)` wyekstrahowany z `check_r18_governance_streak` — wpis scopowany do pierwszego pustego wiersza (`seg.split("\n\n", 1)[0]`); closing prose po ostatnim wpisie nie jest treścią żadnego wpisu. Progi `>3d` WARN / `>14d` FAIL bez zmian (S62); komunikaty FAIL/WARN stringowo identyczne (z `(since ...)`). Rozróżnienie no_date/bad_date zachowane w tuple `(fid, age, entry, reason, raw_date)`.

## M1 (control, poniżej progu)

M1 (control) raw: helper → 1 wpis, age=0 (0 < 3d → brak FAIL/WARN).

Syntetyczny wpis `D-2026-10-18-01`, `PENDING_IMPLEMENTATION`, `zapisano: 2026-10-18`, today=2026-10-18 → helper zwraca 1 wpis, age=0 (0 < 3d → brak FAIL/WARN). Raw: `age=0`.

## M2 (shift, powyżej FAIL)

M2 (shift) raw: helper → age=17 (>14d → FAIL path).

Wpis `D-2026-10-01-01`, `PENDING_IMPLEMENTATION`, `zapisano: 2026-10-01` → age=17 (>14d → FAIL path). Raw: `age=17`.

## M3 (false-positive: WYKONANE + closing prose — regresja S84a)

M3 (false-positive) raw: helper → `[]` (0 FAIL, 0 WARN).

Wpis `D-2026-10-11-04` `WYKONANE` + pusty wiersz + closing prose zawierająca `PENDING_IMPLEMENTATION` → helper zwraca `[]` (0 FAIL, 0 WARN). Raw: `[]`.

## M4 (mixed)

M4 (mixed) raw: helper → tylko `D-2026-10-08-01`, age=10 (WARN path); D-04 nie flagowany.

D-2026-10-08-01 `PENDING_IMPLEMENTATION` (2026-10-08, age 10d → WARN path) + D-2026-10-11-04 `WYKONANE` + closing prose z `PENDING_IMPLEMENTATION` → helper zwraca tylko `D-2026-10-08-01`; D-04 nie flagowany. Raw: `ids=['D-2026-10-08-01'], age=10`.

## M5 (regresja realnego repo)

M5 (regresja) raw: `INTEGRITY_EXIT=0`, 0 linii R18; `Ran 6 tests ... OK`; pełny zestaw `Ran 55 tests ... OK`.

Cały korpus `handoff/flags/session-decision.md` (0 PENDING po `803798b`) → `INTEGRITY_EXIT=0`, 0 linii R18 w outputcie. Dodatkowo `Ran 6 tests ... OK` (M1–M4 + no_date/bad_date) i pełny zestaw `Ran 55 tests ... OK` (test_close + test_build_handoff + R18).

## Przesunięte

Nie ruszałem: progów, komunikatów, `parse_scars` (S76 leak, R21), `split_flags` (S81/S83), `close.py::check_includes` (S84b, nadal otwarte), realnego `session-decision.md`, `803798b` (S78: bez amend/rebase/revert).

Zgodnie z R14: na close nie zabrakło nic; długi jawne poniżej. Po dopisaniu S85 przeprowadzono `ingest_brain.py`: problems: 65 problem(s) w brain.db (`ingest_brain.py --check` zielone)

not checked: S76 leak `parse_scars` (osobny effort R21); S78 retired; S80 candidate; R14 shelf; zakaz `python -c` (S8); S84b `check_includes` `git rm` trap — nadal otwarte; S84a — naprawione tym commitem.

Źródła: `scripts/check_workspace_integrity.py` (`_r18_pending_decisions`), `scripts/test_check_workspace_integrity_r18.py` (M1–M5), `SCARS.md` S85.
