---
type: Concept
flag: root_committed_e61d8c8
since: 2026-10-03
owner: opencode
agent: build
model: opencode/space-bunny-free
origin: this session (commit)
title: root_committed_e61d8c8
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`root_committed_e61d8c8` — 2026-10-03: root w `e61d8c8` (41 plików, +1881/-179) — handoff jako maszyna stanu (flaga = plik = jeden writer, `HANDOFF.md` generowany z `handoff/flags/` + `handoff/deep/` przez `scripts/build_handoff.py`, kontrakt `handoff/CONTEXT.md`), `scripts/session.py` z `--format json` + fallbackiem po basename, `.gitignore` ignorujący `scripts/_scratch/*` poza dwoma zadeklarowanymi helperami, `AGENTS.md` z nową regułą „never change a gate to let a commit pass" i bliznami (d)-(g), deklaracja `handoff/` w `CLAUDE.md` + `ALLOWED_ROOT`. Gate'y przed commitem: `build_handoff.py --check` rc=0, `pytest` 13/13 + 15/15, `check_workspace_integrity.py` rc=0, `git diff --cached --check` czyste. Poza paczką: `scripts/agent_sessions.py` (praca innego agenta, w locie) + `HANDOFF.md`/`STATE.md` do odświeżenia (następny commit). Szczegóły: `handoff_flag_per_file_icm`, `verification_tool_scars`. Next: osobnym commitem z uzasadnieniem — wpięcie `build_handoff.py --check` do `scripts/check_workspace_integrity.py`; decyzja o zadeklarowanym `pytest.ini` (`testpaths = scripts`) czeka.