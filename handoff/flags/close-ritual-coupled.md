---
type: Concept
flag: close-ritual-coupled
since: 2026-10-10
owner: mateusz
agent: opencode
model: opencode/muse-spark-1.3-contributor-free
origin: session-close
title: close-ritual-coupled
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`close-ritual-coupled` — 2026-10-10: iteracja po review warstw: (1) body flagi MUSI zawierać linię `not checked:` (walidowane; puste `—` dozwolone, przemilczenie nie) — przestrzeń negatywna wchodzi do flagi zamiast czekać na recenzenta; (2) `--dry-run` pełny: waliduje `--include` (istnienie) i obce dirty pliki — wcześniej sprawdzał tylko kształt body i bramy, nazwa była myląca; (3) `--amend` zapisany jako kandydat w docstringu (brak trybu poprawek = 2+ commity na flagę z korektą; re-run transakcji celowo zamiast patchowania commita). Testy 8/8 (helpery + `load_body` + `check_includes` + wymóg `not checked`); transakcja dogfoodowana 4. razem.
not checked: close sesji niemodyfikującej close.py; commit z projects/ mimo hooka; --include bez zgadywania (checklist w poprzedniej wersji flagi, nadal otwarta).
