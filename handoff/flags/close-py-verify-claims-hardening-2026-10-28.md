---
flag: close-py-verify-claims-hardening-2026-10-28
since: 2026-10-28
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
---

`close-py-verify-claims-hardening-2026-10-28` — 2026-10-28: Wymuszono obecność sprawdzalnych twierdzeń przy jawnym `--verify-claims`; dodano test `COUNT=5` w `scripts/test_did_sessions.py`.

Stan: Poprzedni commit d62ad7d domknął residue `self-modifications.log`. W tej sesji uszczelniono warstwę weryfikacji w `scripts/close.py`: `verify_claims()` pozostaje czystą funkcją bez zmian zachowania (42 istniejące testy przechodzą), natomiast w miejscach CLI (`dry_run` i `main`) jawne podanie `--verify-claims` przy `rep.re_derived == 0 and rep.gate_covered == 0` kończy się natychmiastowym `fail("verify-claims")`. Dodano test jednostkowy weryfikujący to zachowanie w `scripts/test_close.py` (łącznie 43 passed). Utworzono `scripts/test_did_sessions.py` zabezpieczający domyślną wartość `COUNT=5` w `scripts/did_sessions.bat` przed cichym regresem (1 passed). Integrity gate pozostaje zielony.

Next: Osobna sesja badawcza na `projects/research/benchmark-core/` dla end-to-end FEV runu (`ValueError: inhomogeneous shape` na multi-series).

not checked: FEV end-to-end na benchmark-core (zgodnie z zasadą one project per session odroczone do kolejnej dedykowanej sesji); zachowanie innych harnessów niż opencode.
