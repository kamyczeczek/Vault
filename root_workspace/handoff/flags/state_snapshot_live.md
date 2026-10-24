---
flag: state_snapshot_live
since: 2026-10-03
owner: unassigned
agent: unknown
model: unknown
origin: migrated 2026-10-03 from HANDOFF.md §Status
---
`state_snapshot_live` — 2026-10-03: `STATE.md` w roocie (ICM inv. 9: generowany skan, nie ręka) — HEAD, brudne pliki, ostatnie commity, tabela runów + werdykty, LATEST. Builder: `scripts/build_state.py` (`--selftest` green, stdlib). Odświeżanie: (1) rytuał zamknięcia (`AGENTS.md` — `build_state.py` po `build_handoff.py`), (2) automatycznie przy `review.py --decide` (werdykt zmienia stan). Od 2026-10-03 **oba** pliki są generowane (`build_state.py` + `build_handoff.py`), a narracja ma dom w `handoff/flags/` — jeden fakt, jeden dom, zero ręki w widokach. Next: nic — działa.
