---
type: Concept
flag: review_workflow_live
since: 2026-10-03
owner: unassigned
agent: unknown
model: unknown
origin: migrated 2026-10-03 from HANDOFF.md §Status
title: review_workflow_live
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---
`review_workflow_live` — 2026-10-03: łańcuch odbioru to jedna komenda: `python scripts/review.py .dgc-evidence/runs/<run-id>/` (znajduje REVIEW.md, odpala verify, wkleja rc+summary jako banner zielony/czerwony/szary, renderuje HTML, otwiera przeglądarkę; `--selftest` green). Werdykt jako klik-komenda: `review.py <run-dir> --decide PASS|FAIL|BLOCKED [--note]` zapisuje maszynowo czytelny `DECISION.json` obok REVIEW.md i prze-renderowuje HTML. Per-run layout żyje: `.dgc-evidence/runs/{pstack-research,goose-pstack}-2026-10-03/` (prawdziwe REVIEW przeniesione ze `_scratch`), `runs/LATEST` = goose-pstack (czeka na werdykt); dema `REVIEW_demo/research_demo/gates_demo` skasowane; research-only REVIEW bez claimów pytest dostaje szary banner (nie czerwony). Format REVIEW zaakceptowany („jest okej"). Next: Twoja ocena bieżącego runu (`review.py` + `--decide`) + decyzja o commicie w ARL. 2026-10-03 Twoja recenzja pstack-REVIEW: treść dobra, szkielet niekompletny → poprawione (nagłówek raportu, tabela etapów 00–08 z N/A dla 06/07, kolumna `Sprawdzone 2026-10-03` w portach, zdanie o wersjach na górze) + banner research-only zmieniony z szarego ostrzeżenia na zielony PASS. Selftest + gate green po zmianie. Detale rozproszone wcześniej w `review_renderer_landed` / `root_gate_green_workflow_declared` — scalone tu, tamte wpisy usunięte.
