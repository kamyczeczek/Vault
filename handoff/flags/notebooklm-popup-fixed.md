---
flag: notebooklm-popup-fixed
since: 2026-10-09
owner: Mateusz
agent: agnes-2.5-flash
model: agnes-2.5-flash
---

`notebooklm-popup-fixed` — 2026-10-09: Terminal popup from NotebookLM refresh disabled.
**Corrected 2026-10-10: the 2026-10-09 diagnosis below was wrong** — see
`## Correction` for the real chain.

## Correction (2026-10-10)

The `NOTEBOOKLM_DISABLE_KEEPALIVE_POKE` env var targets the `notebooklm-py`
package (`~/.notebooklm-venv`), which does **not** appear anywhere in the
observed process chain. A 15-minute process watcher (`_nlm_watch.csv`,
session of 2026-10-08) captured the real chain at 15:46:

`svchost.exe (Task Scheduler) → nlm.exe → python.exe → chrome.exe
--remote-debugging-port=9223 --headless=new`

i.e. the scheduled task **`\nlm-auth-refresh`**
(`nlm.exe auth refresh -p piwowarski`, every 30 min, interactive logon).
A console binary launched by the Scheduler in an interactive session gets a
visible console — that flash every 30 minutes is the recurring popup.

## Fix Applied (2026-10-10)

Wrapped the task action in a hidden launcher so no console ever shows:

- Launcher: `C:\Users\Mateusz\.local\bin\nlm-refresh-hidden.vbs` — runs
  `nlm.exe auth refresh -p piwowarski` via `WScript.Shell.Run(..., 0, True)`
  (hidden window, waits, propagates exit code). Invoked through
  `C:\Windows\System32\wscript.exe` (windowless host).
- Task action changed with `schtasks /change /tn "nlm-auth-refresh" /tr ...`
  — schedule (every 30 min), logon mode (interactive), and run-as user
  untouched.

Verification (2026-10-10 ~01:22):

- `schtasks /run /tn "nlm-auth-refresh"` → Last Result **0**, no visible window
  observed; no `nlm.exe`/`python.exe` residue afterwards.
- `NOTEBOOKLM_DISABLE_KEEPALIVE_POKE=1` remains set in User env (harmless, but
  it was never the fix — the popup came from the scheduled task, not from
  `notebooklm-py` keepalive).

## Superseded 2026-10-09 diagnosis (kept for the record)

> The `notebooklm-py` package in `~/.notebooklm-venv` spawns a subprocess via
> `NOTEBOOKLM_REFRESH_CMD` when rotating cookies
> (`_poke_session` → `_rotate_cookies` → `_coalesced_run_refresh_cmd`).
> Set `NOTEBOOKLM_DISABLE_KEEPALIVE_POKE=1` … No more terminal popup expected.

Wrong because `nlm` (`notebooklm-mcp-cli`) is a different package from
`notebooklm-py` and the watcher CSV shows no `notebooklm-py` process in the
chain. The env var was set but the popup recurred on the 30-minute schedule.
Related scar: NotebookLM auth runs through `nlm doctor auth-replay`
(`httpx_ok`), never through the venv.

Notes:
- The `notebooklm-mcp-cli` (nlm v0.15.4) is installed at `~/.local/bin/nlm.EXE`
- Two profiles exist: `default` and `piwowarski` (default is `piwowarski`)
- CDP from Chrome works (saved profiles: default, piwowarski)
- `nlm doctor` shows all green; only "issues" are missing Claude/Cursor/Gemini integrations (not needed)
