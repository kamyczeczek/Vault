---
type: Concept
flag: state-export-levels-fix
since: 2026-10-13
owner: mateusz
agent: opencode
model: oc/claude-3-5-sonnet
origin: session-close
title: state-export-levels-fix
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`state-export-levels-fix` — 2026-10-13: naprawa wielopoziomowego eksportu i rozdzielenie długu procesowego.
- L1-full per-projekt naprawione przez ustawienie `useGitignore: false` w `base.json` (wzorzec `**/*` działa, każdy projekt ≥ 10× L0-entry).
- L0-routing zmniejszony z 240 KB do 32.5 KB (usunięto HANDOFF.md, STATE.md, SCARS.md).
- L1-contracts zoptymalizowany.
- `sessions/` dodane do `.gitignore` w `handoff/state_description/`.
- Retrospektywa zmiany `close.py` (`--error-match` → `--error-unmatch`) z commita `state-export-levels` udokumentowana we flagi i raporcie.
- Untracked pliki sklasyfikowane, cudze wpisane do `not checked:`.

not checked:
- T18-FIX (graphrag.py, measure_trust_set.py, trust_set_results.json) — poza zakresem.
- docs/reviews/session-2026-10-13-kr-*.md, docs/reviews/session-2026-10-13-workflow-verification.md, handoff/real_case_*.md / .jsonl, scripts/memory/queries.jsonl — untracked z innych kontekstów.
