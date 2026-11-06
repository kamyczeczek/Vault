---
flag: dependency-map-2026-11-06
since: 2026-11-06
owner: coding-assistant
agent: antigravity
model: omniroute/agy/claude-sonnet-4-6
---

`dependency-map-2026-11-06` — 2026-11-06: Zbudowano mapę zależności bez kasowania plików.

## Wykonane

- Napisano helper `scripts/_scratch/dependency_map.py` (gitignore'd) — buduje
  mapę inbound-ref dla każdego śledzonego pliku w `scripts/` + mapę doc-referencji
  dla `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`, `MAP.md`.
- Dodano detektor call-site'ów (`call_sites()`) wykrywający split-path subprocess
  calls (`root / "scripts" / "ask.py"`), których grep ścieżki nie łapie.
- Napisano helper `scripts/_scratch/dead_routes.py` — szuka ścieżek wymienionych
  w instrukcjach (skills/, .pi/agents/, AGENTS.md, CLAUDE.md, SCARS.md, itd.)
  które nie istnieją w drzewie.
- Wyniki zapisane w `docs/dependency-map-2026-11-06.md` i w JSON/TXT w
  `scripts/_scratch/` (gitignored).
- `docs/index.md` zaktualizowany o nowe pliki.

## Kluczowe ustalenia

### Wiring ukryty przed grep:
- `scripts/ask.py` i `scripts/debug.py` wywoływane przez
  `.agents/plugins/forge-guardrails/scripts/forge_hook.py:230,238`
  metodą `subprocess.run([..., root / "scripts" / "ask.py", ...])`.
  Klasyfikacja: **ENTRY/GATE**, nie DOC-ONLY.

### Klasyfikacja (142 skrypty):
- ENTRY/GATE = 20 (check_workspace_integrity.py refs=127, close.py=86, memory_index.py=54, …)
- INTERNAL = 85
- INSTRUCTION = 1 (scripts/index.md)
- DOC-ONLY = 9 (brak aktywnych wywołań kodu)
- ZERO = 27 (wyłącznie index.md stuby i fixtures testów)

### Dead routes z powierzchni instrukcji:
- 14 brakujących ścieżek — wszystkie uzasadnione (scar docs, archiwa ARL,
  placeholdery, wzorce konwencji jeszcze nie zrealizowane). Żadna wymagana
  ścieżka nie zniknęła ze workspace.

### DOC REFERENCE MAP — zerowe referencje:
- `handoff/decisions/CONTEXT.md`, `kb/Notes/OKF-rag/CONTEXT.md` — brak live refs.
- Wszystkie `projects/research/*/CONTEXT.md` (5 projektów) poza etth1-h720 i
  the-pragmatic-programmer-retrieval — brak live refs.
- Wszystkie `projects/research/*/MAP.md` (7 projektów) — brak live refs.

## Niewykonane

- Nie usuwano żadnych plików.
- Nie zmieniano `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md` ani żadnych skryptów.
- Nie podjęto decyzji o usunięciu DOC-ONLY / ZERO scripts — wymaga osobnej sesji.
- not checked: GitHub API PR/Issues; archiwum provenance beyond current tree; faktyczne użycie DOC-ONLY scripts przez agentów zewnętrznych.

## Następny krok

Na podstawie tej mapy: ocenić, czy 9 skryptów DOC-ONLY (bez aktywnych wywołań)
lub 27 ZERO (stuby) można bezpiecznie usunąć. Każda decyzja = osobny commit
z uzasadnieniem.
