---
flag: workflow-enforcement-2026-10-13
since: 2026-10-13
owner: mateusz
agent: opencode
model: opencode/muse-spark-1.3-contributor-free
origin: session-close
---

`workflow-enforcement-2026-10-13` — 2026-10-13: cztery mechanizmy egzekwujące SCARS: scan_secrets + pre-commit hook, pre_close_check, verify_report_evidence, close.py body fix.

Deliverables: scripts/scan_secrets.py (czysty na 200 plikach, SECRETS_CLEAN), hooks/pre-commit (skan przed rebuild views), scripts/pre_close_check.py (PRE_CLOSE_READY na dobrym body, PRE_CLOSE_BLOCKED na celowym bledzie), scripts/verify_report_evidence.py (oba raporty bez ## Tool calls = FAIL, test pozytywny przechodzi), scripts/close.py (subject + blank + pelne body, S60 dopisane), docs/workflow/README.md (37 linii, 3 sekcje), mapa (T14-T16, wpis Decisions).

STOP GATE 0: S56/S58/S59/S60/S62 wklejone z transkryptu; close.py linia 279 [:96]; pre-commit: whitespace + rebuild + integrity; zadne z 3 skryptow nie istnialo. HEAD=2ed922f (po kr-hype-final-r19-closed).

not checked: test_gate_rewrite_detector (S62, tylko ticket T16), instruction_triage (tylko ticket T14), stale_views_auto_fix (tylko ticket T15), _tmp_* z eval/ (9 plikow)
