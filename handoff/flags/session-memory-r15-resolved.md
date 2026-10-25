---
type: Concept
flag: session-memory-r15-resolved
since: 2026-10-07
owner: mateusz
agent: agnes-3-flash
model: agnes-3-flash
origin: closing ritual — session-memory R15 resolution
title: session-memory-r15-resolved
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

## Stan

- **R15 (twardy gate) zielony: 15/15, hit@5=1.000, MRR=0.733.** Diagnoza: dryf
  danych, nie regres kodu. 5 świeżych sesji droid (identyczny provider-error
  `cx/gpt-5.6-luna-*` jako pierwsza wiadomość) wypychało kanoniczne
  `8ced867d-a735` / `c5c82ede-91fc` z top-5. Naprawiono dane (Opcja A):
  `exclude_session_ids` w `scripts/memory/eval_queries.json` + support w
  `scripts/eval_memory_retrieval.py`. Progu NIE obniżano.
- **Wszystkie 4 regresje ciche w `scripts/memory_index.py` naprawione i
  zweryfikowane:** `freshness()` (fresh-clone OK / UNVERIFIED / STALE),
  `log_usage` (try/except OSError — kontrakt CONTEXT.md), `--full` (dead flag
  podpięty do `_evidence_snippet`, 400-char evidence per hit), `get`
  (telemetria `found: true/false` + guard metryki dead-chunks w `stats`).
- **Pełny gate zielony** (`check_workspace_integrity.py`): R14 OK, R15 15/15.
- Drzwi (`scripts/debug.py`) + bibliotekarz (`skills/debug-with-memory/`) +
  półka (curated shelf w `memory_index.py`) działają; SKILL.md skorygowany
  (format linii kandydata = chunk_id + date + [type] + heading[:60], bez body).

## Czego NIE zweryfikowano / otwarte

- Per-agent coverage w `freshness()` — celowo usunięte (konflikt z
  `--include-runtime`); otwarte w fladze `session-memory-eval.md`.
- R16 advisory check — **zaimplementowany 2026-10-07** w
  `check_workspace_integrity.py` (advisory, `WARNS` only, gałęzie
  zweryfikowane); opis w fladze `session-memory-eval.md`.
- Loader DSH v4/zstd — zweryfikowany diffem i lekturą, nie end-to-end.
- `handoff/flags/dsh_sessions_parser_and_zstd.md` — wątek parsera DSH
  zakończony w poprzedniej sesji; flaga zostaje jako dokumentacja.

## Next step

Rutynowy ingest wykonany 2026-10-07 02:02 (lag R14: 1:08 → 0:09). Przy
podejściu 90d/2GB — archiwizacja + skasowanie `memory.db` (zgodnie z
"Storage lifecycle" w CONTEXT.md). R16 zamknięty (implementacja, nie
skok) — otwarte pozostały tylko 2 punkty z sekcji powyżej.
