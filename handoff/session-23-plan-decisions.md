# Session 23 — Plan-D decisions (owner, 2026-10-18)

- **Data:** 2026-10-18
- **Status:** PLAN ZAKTUALIZOWANY
- **Zakres:** rozstrzygnięcie findings A1 (always-EN) i M1 (WS3 scope) z `handoff/session-22-plan-audit.md` (`6fd9ca2`); oznaczenie M4/M5/M7/M8 jako DEFERRED. Bez researchu. Bez `--approve` (gates 5/5).

## Decyzja A1 — always EN query

- **Decyzja właściciela:** Tak — always EN; WS2 OUT.
- **Uzasadnienie:** baseline PL 0.827 → EN 0.981 (+8 pytań/52, 0 kosztu latencji; model bge-small-en-v1.5 jest EN-only). WS2 (contextual na PL) traci sens — plan redukuje się do WS1 + WS3.
- **Konsekwencja dla WS2:** OUT — WS2 zachowany jako referencja, nie do wykonania.
- **Zapis w planie:** `handoff/session-17-d-scope.md` §WS2 — adnotacja dodana (WS2 OUT).
- **Zapis w progach:** `handoff/session-21-s56-thresholds.md` §WS2 — adnotacja dodana (próg odnosi się do EN baseline 0.981, potwierdza OUT).

## Decyzja M1 — WS3 scope

- **Decyzja właściciela:** (c) oba — WS3a (metryka) + WS3b (ranking).
- **Konsekwencja:** WS3a (benchmarking metryki comparison, jak w planie) + WS3b (retrieve per topic + RRF — naprawia q012).
- **Zapis w planie:** `handoff/session-17-d-scope.md` §WS3 — WS3a bez zmian + nowa podsekcja WS3b z 6 polami.
- **Zapis w progach:** `handoff/session-21-s56-thresholds.md` §WS3 — adnotacja + nowa sekcja WS3b z progiem MRR +0.02.

## DEFERRED (świadomie odłożone)

- **M4 — MiniLM reranker:** DEFERRED. Powód: Tier 4 (`bge-reranker-base`) wykluczony pomiarem (Zadanie 5, ~10 s/query); MiniLM to inna decyzja wymagająca pomiaru latencji + Recall@8, poza zakresem D.
- **M5 — RAPTOR/graph:** DEFERRED. `data/raptor_tree` istnieje w projekcie, ale nie jest referencjonowany; `graph.db` nie istnieje. Potencjał niewykorzystany — do osobnej sesji diagnostycznej (~15 min odczytu) poza zakresem D.
- **M7 — HyDE:** DEFERRED. P3, dodaje LLM w pętli (~1–3 s/query), dyskwalifikuje w produkcji realtime.
- **M8 — query expansion / multi-query:** DEFERRED. P3, latencja ×N, koszt nieproporcjonalny do zysku przy 0.981.

## Findingi z sesji 22 — status po decyzjach

| Finding | Status po sesji 23 |
|---|---|
| A1 (always EN niezapisane) | ROZSTRZYGNIĘTE — Tak (always EN; WS2 OUT) |
| M1 (WS3 mismatch) | ROZSTRZYGNIĘTE — (c) oba (WS3a + WS3b) |
| M4/M5/M7/M8 (poza planem bez adnotacji) | DEFERRED (świadomie odłożone) |
| D1 (zależności) | BRAK — wszystkie istnieją |
| S21-x (progi) | BRAK — wszystkie zapisane |

## Finalny stan

- Plan D: `handoff/session-17-d-scope.md` zaktualizowany (WS2 OUT, WS3b dodane, DEFERRED).
- Progi S56: `handoff/session-21-s56-thresholds.md` zaktualizowane (WS2 EN adnotacja, WS3b próg).
- Research: NIE wykonany.
- A/B/C/D/E: bez zmian.
- **Następny krok:** research WS1 (chunk-level sufficiency, ~4 h) — po zatwierdzeniu decyzji.