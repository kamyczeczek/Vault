---
flag: preflight-agent-and-s71-scar-2026-10-28
since: 2026-10-28
owner: mateusz
agent: opencode
model: omniroute/agy/gemini-3.8-flash-high
origin: session-close
---

`preflight-agent-and-s71-scar-2026-10-28` — 2026-10-28: Wprowadzono S71 do `SCARS.md` i zindeksowano w `brain.db` (50 wpisów problemów). Wdrożono deterministyczny preflight agenta `scripts/preflight_agent.py` z testami jednostkowymi `scripts/test_preflight_agent.py` (5/5 zielone). Skrypt czyści deadlockujące locki `.unlazy/locks` i `.git/index.lock` oraz mierzy czas reakcji interpretera Pythona (< 2.5 s) i polecenia git (< 5.0 s). 47 testów w pakiecie `test_close.py` i `test_preflight_agent.py` przechodzi.

not checked: automatyczny hook wpięty przed każdą sesją w konfiguracji harnessu (wymaga kroku 3 i 4).
