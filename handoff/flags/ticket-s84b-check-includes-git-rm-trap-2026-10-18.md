---
type: Concept
flag: ticket-s84b-check-includes-git-rm-trap-2026-10-18
since: 2026-10-18
owner: mateusz
agent: opencode
model: opencode/glm-5.3-flash-free
origin: owner-recommendation after r18-parser-scope-fix-2026-10-18 (8af7e77)
title: ticket-s84b-check-includes-git-rm-trap-2026-10-18
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`ticket-s84b-check-includes-git-rm-trap` — 2026-10-18: Ticket otwarty decyzją ownera (łańcuch E4 zamknięty na `8af7e77`).

Stan: `check_includes` (`close.py:435-444`) wymaga `exists_on_disk or is_tracked`; `git rm` zabiera plik **z obu**, więc retire przez `git rm` + `close.py --include <path>` kończy się `--include not found under workspace root or git index` (`CLOSE_EXIT=1`) — pierwszy agent, który to zrobi, debuguje od zera. Poprawna kolejność dziś (dokumentowana w S84, Problem B): plain `rm` (worktree ` D`), potem close `--include` → `git add` staguje deletion.

Next step: albo dokumentacja (doprecyzować S84/zasady retire), albo fix w `close.py` (uznaj deletion-in-index jako legalne `--include`). Decyzja ownera: fix vs doc. Test na scenariuszu `git rm` obowiązkowy, jeśli fix.

not checked:
- **S86 (candidate)** — wzorzec re-deriwowalnego claimu w `--verify-claims`: present-tense counter + jednostka zaczynająca się od `flag|plik|problem|scar|decyzj...` + nazwany artefakt (`brain.db`, `handoff/flags/`) w **tej samej klauzuli** (`scripts/close.py::_counter_artifact`; transition `64 → 65` w klauzuli wyłącza re-derywację). Dopisać do `handoff/CONTEXT.md` przy okazji najbliższej sesji ruszającej close-pipeline.
