---
type: Concept
title: results_bigdict_lasso_experiment
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# BigDict-LASSO Experiment Results

## Hypothesis
LASSO regression can automatically select useful features from the expanded filter bank, eliminating the need for manual ablation of wavelet detail coefficients.

## Implementation
- Used same 19-filter bank as BigDictELM
- Applied LASSO with cross-validation for automatic feature selection
- Used only consistent windows (D=1824) to avoid pywt boundary issues

## Key Findings

### Feature Selection by LASSO
- LASSO selected X out of 1824 features (need final count)
- Ideally should remove wavelet detail coefficients automatically

### Performance Comparison
| Task | BigDict-Ridge (Opt) | BigDict-LASSO | Winner |
|------|---------------------|---------------|--------|
| thomas_H24 | 0.0195 | TBD | ? |
| seasonal_H48 | 0.3059 | TBD | ? |
| multiscale_H96 | 0.2251 | TBD | ? |

## Technical Challenge
pywt.swt requires even-length input signals. Windows near the end of series may have odd lengths, causing inconsistent feature dimensions.

**Solution**: Skip windows where `total_D != 1824`.

## Next Steps
1. Complete the experiment run
2. Analyze which features LASSO selects
3. Compare auto-selection vs manual removal of detail coefficients
4. Consider expanding feature set with polynomial/interaction terms

## Paper Integration
LASSO's automatic feature selection provides an elegant solution to the wavelet detail toxicity problem — no need for manual ablation if LASSO learns to zero out those coefficients.
