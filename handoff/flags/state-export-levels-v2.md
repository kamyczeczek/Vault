---
type: Concept
flag: state-export-levels-v2
since: 2026-10-14
owner: mateusz
agent: opencode
model: oc/claude-3-5-sonnet
origin: session-close
title: state-export-levels-v2
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`state-export-levels-v2` — 2026-10-14: chirurgiczny fix eksportu. base.json przywrócone `useGitignore: true` + `**/.git/**`; projects.json (nowy) dla per-projekt. L1-contracts 506 KB (był 845 KB), L2-full 3.6 MB (był 260 MB), retrieval-v2 31.6 MB (corpus 10,228 files). Retrospektywna flaga `close-py-ls-files-flag-fix-retrospective` pozostaje z długiem w mapie (brak domknięcia przez konflikt z istniejącym plikiem w repo).

not checked:
- T18-FIX (poza zakresem).
- Cudze untracked pliki w docs/reviews i handoff/.
