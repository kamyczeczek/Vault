---
flag: raw-sessions-dsh-included-2026-11-06
since: 2026-11-06
owner: mateusz
agent: deepseek-harness
model: nvidia/stepfun-ai/step-5-preview
origin: user request (m00002): "zrób by skrypt scripts/raw_sessions_drive.bat uwzględniał też sesje z deepseek harness"
---

`flag` — 2026-11-06: `scripts/raw_sessions_drive.bat` teraz eksportuje też sesje DeepSeek Harness.
Przyczyna, dla której ich nie uwzględniał: `scripts/extract_exact_sessions.py` (ten, który napędza .bat)
szukał sesji DSH w `~/.deepseek-harness/sessions` — katalog istnieje, ale jest pusty (0 plików).
Prawdziwy store to `~/.dsh/sessions/`, a sesje są zapisane jako `session.v4.jsonl.zstd`
(zstd + format v4 z kluczami `type`/`data`/`time`), których stary skan `rglob("*.jsonl")`
i tak by nie odczytał. Naprawa nie polega więc na samej ścieżce, ale na użyciu
sprawdzonego loadera `agent_sessions.load_deepseek_sessions` (ten obsługuje zstd, v4
oraz filtrowanie do aktualnego workspace'u).
Zmiany w `scripts/extract_exact_sessions.py`: nowy `render_dsh(session, f)` wypisujący
`text_markdown` z SessionItem (border agent/model/cwd/msgs/czas/file), merge DSH do
wspólnej listy z timestampem (`updated_at`, fallback na `mtime` raw_path), dispatch
`elif kind == "dsh"`, usunięcie martwego `DSH_DIR` i wpisu `"dsh"` ze skanu katalogów.
Weryfikacja: `python scripts/raw_sessions_drive.bat 3` → 148 KB, 3 najnowsze sesje to
wszystkie DSH (`session-d3c98f6d…`, `session-9f4cae1b…`, `session-f98d7c1e…`),
206 wyrenderowanych tur `## [role]` w `scripts/_scratch/sessions/02_products/raw_sessions.md`.
Next step: brak — działa end-to-end wraz ze sync do `G:\My Drive`.
not checked: pełna suite testów dla agent_sessions.py; sesje spoza bieżącego workspace'u.
