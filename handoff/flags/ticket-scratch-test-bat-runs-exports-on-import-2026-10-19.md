---
flag: ticket-scratch-test-bat-runs-exports-on-import-2026-10-19
since: 2026-10-19
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: review fazy 3 (R5) + pomiar własny podczas fixu transkryptu (P1–P6)
---

`ticket-scratch-test-bat-runs-exports-on-import` — 2026-10-19: Ticket otwarty przy fixie transkryptu (P1–P6). **Korekta atrybucji z review fazy 3**: `exports.md` mutuje nie `check_workspace_integrity.py`, lecz import `_scratch/test_bat.py` podczas kolekcji pytest.

Stan: `scripts/_scratch/test_bat.py` (10 linii, bez funkcji testowej) uruchamia `handoff/state_description/refresh-exports.bat --no-pause` na poziomie modułu. `python -m pytest scripts/` importuje każdy `test_*.py` w drzewie (także `_scratch/`) na etapie kolekcji → odpala `run_exports.py` → regeneruje `handoff/state_description/txt_files/**` i nadpisuje trackowany `handoff/state_description/exports.md` (timestamp + rozmiary L0/L1/L2). To ten sam kształt co cichy side-effect bramki (S28/S56): twierdzenie „bramka mutuje drzewo" nie miało pokrycia w toolcallu.

Pomiar: `git checkout -- handoff/state_description/exports.md` (drzewo czyste) → `python -m pytest scripts/` → `exports.md` zmieniony. Kontrola: po revertcie dwa kolejne `python scripts/check_workspace_integrity.py` zostawiają plik bit-identyczny (SHA256 `FF6F41F0…`).

Next step: albo przenieść `test_bat.py` poza zbierany zakres, albo dodać `if __name__ == "__main__":` / `__test__ = False`, żeby import w kolekcji nie miał side-effectu. Decyzja ownera: guard vs przeniesienie. Gate: dowód, że `pytest scripts/` nie zmienia `exports.md`.

not checked:
- **S82-adjacent** — czy inne skrypty w `scripts/_scratch/` mają side-effecty wykonywane przy imporcie (przegląd całej `_scratch/` poza zakresem tej sesji).
