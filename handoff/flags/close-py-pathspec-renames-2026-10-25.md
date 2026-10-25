---
flag: close-py-pathspec-renames-2026-10-25
since: 2026-10-25
owner: mateusz
agent: codex
model: openai/gpt-6
origin: session-close
---

`close-py-pathspec-renames-2026-10-25` — 2026-10-25: wypchnięto 10 commitów cleanupu; `origin/master` doszedł do `62137c3`.
Naprawiono `scripts/close.py`: brakujące include rozwija do śledzonych ścieżek z indeksu i stage'uje bez rozszerzania zakresu; status NUL parsuje rename/copy jako osobne ścieżki.
Dodano regresje dla usuniętego katalogu, staged deletion katalogu i rename'u. `python.exe scripts/test_close.py` — 39 testów OK. `SCARS.md` dostał regułę S70.
Retired flagę `workspace-gate-repair-2026-10-25`, której następny krok (commit zmian) był już wykonany.
Next: odświeżyć review research-engine na aktualnym drzewie, potem wdrożyć kierunek A — protokół ewaluacji.
not checked: nie zmieniano research-engine; nie uruchomiono ani nie oceniano jego benchmarku.
