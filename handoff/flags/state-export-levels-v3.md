---
flag: state-export-levels-v3
since: 2026-10-14
owner: mateusz
agent: opencode
model: oc/claude-3-5-sonnet
origin: session-close
---

`state-export-levels-v3` — 2026-10-14: domknięcie eksportu. retrieval-v2/L1-full 31.65 MB → 82,336 B (exclude corpus/). L1-contracts zdiagnozowany: winowajca HANDOFF.md (174 KB) oraz agentic-research-lab/MAP.md (115 KB). Raport sesji 4 poprawiony (etth1-h720: OK → WYJĄTEK 6.9×). Mapa: T18/T19 → T-L1-contracts-size/T-retrieval-v2-corpus. Retrospektywna flaga `close-py-ls-files-flag-fix-retrospective` domknięta.

not checked:
- T18-FIX (poza zakresem).
- Cudze untracked pliki w docs/reviews i handoff/.
