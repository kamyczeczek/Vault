# Session 21 — S56 thresholds decision (owner, 2026-10-18)

- **Data:** 2026-10-18
- **Status:** PROGI ZATWIERDZONE
- **Zakres:** trzy progi wstępne z `handoff/session-17-d-scope.md` (Workstream 1/2/3), zatwierdzone przez właściciela w sesji decyzyjnej. Bez researchu. Bez `--approve` (gates 5/5).

## Decyzje właściciela

### Workstream 1 — Chunk-level sufficiency diagnoza (~4 h)

- **Metryka:** odsetek top-8 chunków w trudnych pytaniach (q010, q012 i pokrewne), które po klasyfikacji są `prose` i zawierają pełny passus odpowiedzi (walidacja ręczna n=10–15).
- **Próg (ZATWIERDZONY bez zmian):** diagnoza użyteczna, jeśli **≥20%** top-8 chunków w trudnych pytaniach jest niepełnych semantycznie. Poniżej → hipoteza „chunk-level sufficiency" odpada, D zamykamy ponownie.
- **Koszt:** ~4 h (klasyfikacja + walidacja ręczna + raport).

### Workstream 2 — Contextual retrieval augmentacja (~2 h)

- **Zmiana względem planu:** **NIE** zatwierdzono progu +0.02 Recall@8 any. Wybrano metrykę **(c) MRR** (najczulsza na ranking; baseline 0.895; +0.02 realne). Opcja alternatywna (b) primary Recall odrzucona; opcja „zostań przy any, ≥+0.019 (+1 pytanie)" odrzucona.
- **Metryka:** **MRR** (na EN gold secie, 52 answerable), dodatkowo Recall@8 any + primary, latencja p50/p95.
- **Próg (ZATWIERDZONY):** zysk **≥ +0.02 MRR** przy **p95 ≤ 2× baseline (≤ 260 ms)**. Inaczej odrzucić.
- **Koszt:** ~2 h (re-embedding + re-eval).

**Aktualizacja (sesja 23, 2026-10-18):** A1 = Tak (always EN). Próg MRR +0.02 odnosi się do EN baseline 0.981 (nie PL 0.827). To potwierdza OUT WS2 — brak realnej przestrzeni na +0.02. Decyzja: `handoff/session-23-plan-decisions.md`.
### Workstream 3 — Multi-topic comparison benchmarking (~2 h)

- **Próg (ZATWIERDZONY):** wariant (c) „primary = zbiór topiców" musi być spójny z ręcznym odczytem (sesja 5) na **≥80%** comparison. Inaczej wracamy do (b) lub retired (T13/S64).
- **Dopisek (ZATWIERDZONY):** ręczny odczyt rozszerza się na **wszystkie 6 comparison** (q010, q012 i pokrewne). To część ~2 h pracy WS3, nie dodatkowy koszt.
- **Koszt:** ~2 h (definicja + re-eval + raport).

### Workstream 3b — Retrieve per topic + RRF (ranking fix) (~2 h)

- **Metryka:** MRR, Recall@8 any + primary, latencja p50/p95.
- **Próg (ZATWIERDZONY, sesja 23, M1 = (c)):** zysk **≥ +0.02 MRR** (lub +0.019 Recall@8) przy **p95 ≤ 2× baseline (≤ 260 ms)**. Inaczej odrzucić.
- **Koszt:** ~2 h (implementacja + re-eval).

**Aktualizacja (sesja 23, 2026-10-18):** WS3b dodane decyzją M1 = (c) oba. Decyzja: `handoff/session-23-plan-decisions.md`.
## Kolejność wykonania (zatwierdzona)

1. Workstream 1 (diagnoza) — ustala, czy problem jest realny.
2. Workstream 3 (benchmarking metryki) — niezależny od 1/2, może iść równolegle.
3. Workstream 2 (contextual) — zależy od wyniku 1.

## Status

- **Plan:** gotowy (sesja 17) + progi zatwierdzone (sesja 21).
- **Wykonanie:** NIE wykonane. Trzy osobne sesje research, po tej decyzji.
- **Następny krok:** sesja research — Workstream 1 (chunk-level sufficiency diagnoza).

## Powiązania

- `handoff/session-17-d-scope.md` — plan D (3 workstreamy, 6 pól każdy).
- `handoff/session-13-owner-decision.md` — E = Tak (2026-10-18), commit `692a121`.
- `handoff/session-19-audit-plan-d.md` — audyt sesji 18 (POTWIERDZONY).
- `handoff/session-20-audit-closeout.md` — audyt domknięcia (DOMKNIĘTY).