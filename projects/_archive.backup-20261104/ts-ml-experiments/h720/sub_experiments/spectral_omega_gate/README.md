---
type: Concept
title: README
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Spectral Predictability Ω Gate (Phase 1)

Prototyping the no-training Ω stratification gate on ETTh1 H=720 per `RESEARCH/2026-09-12_omega-h720-integration.md` and `RESEARCH/2026-09-12_spectral-predictability-omega.md`.

## Re-run
```bash
python rolling_arm.py
```

## Findings Summary
- Re-derived S-26 anchor: MAE = 1.9909, RMSE = 2.4710 (exact match).
- Ω_336 distribution: Val mean = 0.5036 (P(Ω<0.4) = 10.0%, P(Ω>0.5) = 46.6%), Test mean = 0.5478 (P(Ω<0.4) = 0.3%, P(Ω>0.5) = 76.1%).
- Shift: Val→test shift relative to val std = 0.519σ.
- Residual correlation: Spearman ρ(Ω_336, S-26 MAE) = -0.1119 (p = 1.84e-07).
- Stratified MAE: Regime A (<0.4, n=7) = 2.4348; Regime B (0.4–0.5, n=510) = 2.1156; Regime C (>0.5, n=1644) = 1.9503.
- Orthogonality check: Spearman ρ(Ω_336, volatility) = 0.7975 (high correlation with window standard deviation / volatility).
