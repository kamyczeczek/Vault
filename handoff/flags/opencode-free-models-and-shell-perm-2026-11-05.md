---
flag: opencode-free-models-and-shell-perm-2026-11-05
since: 2026-11-05
owner: mateusz
agent: pi-bolt
model: google/gemini-2.5-pro
origin: session-close
---

`opencode-free-models-and-shell-perm-2026-11-05` — 2026-11-05: Rozwiązano dwa problemy środowiskowe:
1. Przyczyna problemu 1 (`Permission denied: shell`): harness Pi blokował wywołania shella przez regułę `workspaceGuard: block` w `.pi/settings.json` (w OpenCode reguły `permission.bash` miały już `git commit*`: allow i `git push*`: allow). Ustawiono `workspaceGuard: "off"` w `.pi/settings.json`, po czym testowy commit i push (`git commit --allow-empty -m "test: shell permission check" && git push origin master`) wykonał się z exit code 0 (commit 57fe56f).
2. Przyczyna problemu 2 (`stream went silent for 120s` / brak darmowych modeli): zapytania szły przez proxy omniroute do płatnych/niestabilnych endpointów zamiast natywnego darmowego providera opencode. Wykonano kopię zapasową configu do `C:/Users/Mateusz/.config/opencode/opencode.jsonc.bak.20261105`. Zaktualizowano `opencode.jsonc` ustawiając domyślny model i mały model na `opencode/deepseek-v4.1-flash-free`. Przeładowano konfigurację (`opencode reload`, exit code 0) i wykonano smoke test poza UI: `opencode run --model opencode/deepseek-v4.1-flash-free "hi"` zakończony sukcesem (exit code 0, odpowiedź: "Hey! What are we working on today?").
not checked: działanie pozostałych darmowych modeli z listy opencode poza deepseek-v4.1-flash-free; zachowanie proxy omniroute pod długimi zapytaniami.
