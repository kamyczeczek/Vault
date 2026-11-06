---
flag: dead-script-candidates-2026-11-06
since: 2026-11-06
owner: Mateusz
agent: deepseek-harness
model: nvidia/stepfun-ai/step-5-preview
---

`dead-script-candidates-2026-11-06` — 2026-11-06: Sesja 3 planu (script pruning analysis) zamknięta jako **raport** — bez kasowania. Raport: `docs/dead-script-candidates-2026-11-06.md` (wpis w `docs/index.md`).

## Wykonane

- Potwierdzono liczbę: 143 śledzonych plików w `scripts/` bez `_scratch/` = 142 skrypty + `scripts/index.md` (mapa z `91a7f6a` liczyła index.md w osobnym koszu INSTRUCTION — stąd 142 vs 143; drzewo skryptów niezmienne od mapy).
- Odświeżono licznik referencji dla 12 kandydatów (`git grep -l`, pliki nie-`_scratch`, sam plik wykluczony): wszystkie trafienia tylko w markdown/docs/index — **zero wywołań z kodu**.
- Rekomendacja raportu: 4 kandydaci do usunięcia po zgodzie właściciela (`move_state_description.py`, `gate_checks.py`, `check_kb_layout.py`, `debug_skill_resources.mjs` — ten ostatni z zastrzeżeniem: konfiguracja `~/.pi` jest poza repo), 3 narzędzia do decyzji (`dump_agent_config.py`, `smoke_load_deepseek.py`, `smoke_zstd.py`), reszta (testy pytest, `.bat` właścicielski, `queries.jsonl`) = trzymać.
- Procedura usuwania zapisana w raporcie: jeden skrypt = jeden commit z dowodem (0 refs + tier), po każdym `check_workspace_integrity.py` + `build_handoff.py --check`.

## Ryzyka / not checked

not checked:
- Wywołania z konfiguracji poza repo (`~/.pi`, `~/.config/opencode`, globalne hooki) — ref-scan widzi tylko pliki śledzone w Vault.
- Rzeczywiste uruchomienia skryptów przez agentów zewnętrzne (poza tym repozytorium).
- Decyzja o usunięciu któregokolwiek pliku — nie podjęta, nie moja do podjęcia.

## Następny krok

Decyzja właściciela po raporcie: zatwierdzić 4 kandydatów (usuwanie = osobne commity) albo odrzucić. Potem Sesja 4: rozstrzygnięcie obcej zmiany `COUNT=5 → 1` w `scripts/raw_sessions_drive.bat`, i Sesja 5 (walk-test).
