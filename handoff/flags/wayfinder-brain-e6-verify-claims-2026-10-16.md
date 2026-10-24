---
flag: wayfinder-brain-e6-verify-claims-2026-10-16
since: 2026-10-16
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
---

`wayfinder-brain-e6-verify-claims-2026-10-16` — 2026-10-16: `close.py --verify-claims` wdrożone (decyzja B3). Re-derywuje tylko twierdzenia z wykonywalnym artefaktem: `commit <hash>` (root + repo zagnieżdżone pod `projects/`), licznik z nazwanym artefaktem (`handoff/flags/*.md`, `brain.db:<tabela>`), gate claim (counted, nie re-uruchamiany). W `--dry-run` FAIL = exit 1 (fail-loud), w real close FAIL = WARN (nie blokuje). Guardy przeciw fałszywym FAIL-om: clause scoping (zdanie, nie okno znaków), transition guard (historical change → WARN), commit-diff guard (licznik diffa commita → WARN). Korpus 168 flag po guardach: 2 prawdziwe dryfy (`wayfinder-brain-e7-expect-hash` 48→50 problems, `workflow-verification-fix` nieistniejący `fd9cb99`), 0 fałszywych. 14 nowych testów w `test_close.py` (28 zielonych). S72 w `SCARS.md` (clause-scoping false-FAIL, silent WARN w dry-run, nested-repo commit resolution). `docs/wayfinder-brain-answers/E6-verify-claims.md` z raw outputem i `not checked:`.

not checked: real close z `--verify-claims` (WARN-only, nie blokuje) — nie wykonany live; ścieżka to ta sama funkcja z niższym progiem. `check_workspace_integrity.py` po tym commicie (close uruchamia go).
