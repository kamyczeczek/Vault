---
type: Concept
title: LONGTERM_ETTH1_H720_DESIGN
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# S49 — ETTh1 H720 Long-Term Specialist Methods (design-first, PRE-REGISTERED)

**Status:** pre-registration (binding, S43-P1 discipline). Code + run land in the same PR as results.
**Execution status (2026-10-29):** S49 line CLOSED (REJECT). All three candidates (SAB-L, H2K, AMR-24/168) completed, evaluated and rejected. Meta-H selector not run. Detailed protocol fidelity audit and closeout documented in ADR 0001 (`docs/adr/0001-s49-closeout-and-protocol-discrepancies.md`) and the Execution Annex below.
**Motivation (per `REFLECTION_PROMISING_METHODS.md`):** H720 ETTh1 is saturated — incumbent S44 `1.9781`, S46/S48 REJECTED. Our members were tuned at H24–H336; H720 (30 days) breaks motif phase alignment and makes single-ridge 720-dim readouts ill-conditioned. The gap is a *long-horizon architecture*, not another ELM width bump.

## Suite (pre-registered)
- **Task:** ETTh1 H720 rolling, **W=20 locked eval origins** + separate dev origins for any selection (leakage-safe). Train slice identical to S44 (same cutoff, same normalization).
- **Variability:** frozen-random components (ELM/ESN-style dicts) → **5 seeds**, report mean±std.
- **Reporting:** raw MAE **and** normalized MAE (scale must always be stated — reflection finding #1).
- **Regression suite:** every member also run at H96/H336 (gate G3).

## Members (new, H720-specialized — build on proven components only)
1. **H2K — Horizon-Decomposed Drift-Corrected KNN**: split H720 into 3×240 segments. Per segment: detrended motif-KNN on residuals + linear drift carry-forward (level anchored on previous segment's last-24h mean). Exploits KNN's cyclical strength; fixes long-horizon phase drift.
2. **SAB-L — Signal-Adaptive BigDict Long**: scale-mismatch-optimized filter bank (standardized cD* + compact config per the ablation), **L=336 context**, horizon-**grouped** ridge readouts (heads H∈{24,48,96,…} — never one 720-dim ridge), 5 seeds.
3. **AMR-24/168 — Multi-Scale AMR-FBS Envelope**: FFT envelope on 24h + 168h harmonics + weekly drift anchor (7-day mean level); per-horizon ridge. Extends the only method that already wins H720 normalized (0.473 vs DLinear 0.602).
4. **Meta-H (optional, last)**: leakage-safe per-horizon-block selector over {H2K, SAB-L, AMR-24/168}, fitted on dev origins only.

## Completed candidates
- **SAB-L:** rejected after the two-iteration kill budget; final locked mean raw MAE 4.4611.
- **H2K:** implemented, tested, and evaluated under the early-dev/locked-final protocol; final mean raw MAE 2.7270, not promoted. See `H2K_H720_RESULT.md`.
- **AMR-24/168:** implemented (weekly level anchor), selected on early dev origins, evaluated on the locked 12-origin sliding suite; final mean raw MAE 3.1480 (std 1.3573). G1 FAIL, G2 FAIL, G3 PASS. Rejected. See `AMR_24_168_H720_RESULT.md`.
- **Meta-H:** nie uruchomiono; zamknięto wraz z linią S49 po wyczerpaniu budżetu poszukiwań (kill budget).

## Gates (binding, pre-registered)
- **G1:** mean rolling MAE (raw) H720 **< 1.9781** (incumbent S44).
- **G2:** beat DLinear and SpectralFFT at H720 (raw).
- **G3:** no-regression — H96/H336 MAE within +5% of that member's S47-pool best (a long-term specialist must not be a regime-breaker).
- **G4 (diagnostic):** mean rank ≤ 2 across {members + SOTA baselines} at H720.
- **PASS = G1 ∧ G2 ∧ G3.** All members fail → **REJECT S49** after the 2-iteration kill budget (Fail Fast & Cheap; S46/S48 precedent).
- Null-result clause: incumbent gap < 0.02 normalized → treat as saturation, not win.

## Pre-registered risks & mitigations
- Saturation ceiling (mitigated by null-result clause + G3 regression guard) · selection leakage (dev-only, seeds locked pre-run) · 720-dim ridge conditioning (horizon-grouped heads) · KNN hyperparameter fragility (per-dataset k pinned, stability sweep k∈{5,12,24,48}).
- **Dependency:** P0 BigDict standardization control must precede SAB-L (its feature bank depends on the control's verdict).

## Effort
Each member ≈ <1 day CPU; full S49 suite ≈ 20–40 min (matches project "seconds-to-minutes" charter).

## Aneks wykonawczy (2026-10-29): Rozbieżności protokołu i formalne zamknięcie S49

Na podstawie audytu zgodności wykonania z pre-rejestracją oraz ADR 0001 (`docs/adr/0001-s49-closeout-and-protocol-discrepancies.md`) odnotowuje się następujące ustalenia metodyczne:

1. **Liczba originów (20 w planie vs 12 w wykonaniu)**: Pre-rejestracja w sekcji Suite deklarowała `W=20 locked eval origins`. Faktycznie zaimplementowany i uruchomiony protokół w skryptach `run_h2k_h720_final.py` oraz `run_amr_h720_final.py` objął zestaw 12 originów kroczących co 720 h (od 8640 do 16560 z 360-dniowym oknem treningowym).
2. **Liczba seedów (5 w planie vs 1 w głównych wynikach)**: Pre-rejestracja zakładała raportowanie 5 seedów (mean±std) dla komponentów losowych. Główne tabele wynikowe w `H2K_H720_RESULT.md` i `AMR_24_168_H720_RESULT.md` zaraportowały wyłącznie pojedynczy `seed 42`. Pięć seedów zbadano jedynie w diagnostycznym rankingu G4 dla AMR-24/168 (`results/etth1_h720_amr24168_g4.json`).
3. **Porównywalność progu S44 (1,9781)**: Próg 1,9781 z S-44 pochodzi z 3-modelowego blendu (`NLinear + PatchTST-Delta`) testowanego na 2161 gęstych originach (step=1). W S49 nałożono ten próg na pojedyncze modele badane na 12 rzadkich originach (step=720). Jest to rozbieżność metodyczna uniemożliwiająca bezpośrednie porównanie pomiarów. Nie uprawnia to do niepopartego dowodem twierdzenia, że żaden pojedynczy model nigdy nie osiągnie 1,9781. Jednak empirycznie na tym zestawie żaden kandydat (H2K 2,7270; AMR-24/168 3,1480; SAB-L 4,4611) nie osiągnął poziomu prostych baselinów: BigDictELM L96 (2,4777) ani DLinear (2,5384).
4. **Meta-H**: Opcjonalny selektor Meta-H nie został uruchomiony. Ze względu na brak przewagi poszczególnych kandydatów nad baselinami, budowa ensemblingu na odrzuconych modelach została zaniechana i formalnie zamknięta.
5. **Werdykt końcowy**: Linia S49 zostaje formalnie **ZAMKNIĘTA (REJECT)** jako nieudany etap poszukiwania modelu do promocji pod zastosowanym protokołem. Pierwotny tekst pre-rejestracji powyżej zachowano w niezmienionym kształcie jako trwały ślad hipotez badawczych.
