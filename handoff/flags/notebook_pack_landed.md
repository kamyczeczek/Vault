---
flag: notebook_pack_landed
since: 2026-10-07
owner: mateusz
agent: opencode
model: opencode/muse-spark-1.3-contributor-free
origin: notebooklm export workstream (nlm CDP migration)
---

`notebook_pack_landed` — 2026-10-07: przepływ NotebookLM przełączony ze zepsutego `notebooklm-py` (Chrome 127+ App-Bound Encryption: `token_fetch: false`) na `nlm` 0.15.4 (`notebooklm-mcp-cli`, auth przez CDP z żywej sesji Chrome, profil `piwowarski` = `piwowarski.mateusz99@gmail.com`, ustawiony jako domyślny przez `nlm login switch piwowarski`). `scripts/notebook_push.py` zaadaptowany: backend `nlm source add <nb> --file <path> -p piwowarski --json` (schemat `{"source_id": ...}`), wait przez polling `source list` do `status: 2` (brak `source wait` w nowym CLI). Zweryfikowane end-to-end 2026-10-07: `doctor auth-replay` → `httpx_ok` 4/4, jeden plik `nlm-test.txt` + wrapper `--wait` → `ready`, pliki testowe usunięte (notebook ma z powrotem 5 oryginalnych źródeł). Auto-refresh: scheduled task `nlm-auth-refresh` co 30 min (`nlm auth refresh -p piwowarski`). Fallback: `C:\Users\Mateusz\.notebooklm-venv` (nie usuwać), `scripts/notebook_mcp.py` (referencja). Next: `notebook_push.py --auto --sessions N` dla pełnego batcha + doklejenie źródeł eksperckich w NotebookLM.
