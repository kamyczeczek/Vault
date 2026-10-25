---
type: Concept
flag: notebooklm-auth-fixed
since: 2026-10-09
owner: Mateusz
agent: agnes-2.5-flash
model: agnes-2.5-flash
title: notebooklm-auth-fixed
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`notebooklm-auth-fixed` — 2026-10-09: NotebookLM auth working via `nlm` CLI (jacob-bd).

## Status: RESOLVED

The `notebooklm-py` package (`~/.notebooklm-venv`) has been replaced by `notebooklm-mcp-cli` (nlm v0.15.4) as the primary backend per CONTEXT.md.

## Verification
- `nlm doctor auth-replay` → **httpx_ok** (all 4 checks pass: httpx_saved, httpx_after_rotate, httpx_fresh, cdp_in_page)
- `nlm notebook query a49ff8cb... "What is the current date?"` → Today's date is October 9, 2026
- `notebook_push.py --auto --sessions 3` → **OK: all registered** (pack built, 3 sessions exported, 4 files registered, 1 pruned)

## Profile
- Default: `piwowarski` (piwowarski.mateusz99@gmail.com)
- Storage: file mode, cookies present (55)
- CDP from Chrome: available (saved profiles: default, piwowarski)
- Notebooks accessible: 5

## Scripts
- `scripts/notebook_push.py` — uses `nlm` CLI (correct backend)
- `scripts/build_notebook_pack.py` — builds .txt pack files
- `scripts/agent_sessions.py` — exports session files
- Fallback: `~/.notebooklm-venv` kept but not required for daily use

Notes:
- Chrome 127+ App-Bound Encryption broke `notebooklm-py` cookie reads — that's why we migrated to CDP via `nlm`
- The terminal popup issue (keepalive refresh) is fixed separately via `NOTEBOOKLM_DISABLE_KEEPALIVE_POKE=1`
