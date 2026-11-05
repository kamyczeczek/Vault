from pathlib import Path
p = Path("bench.py")
text = p.read_text(encoding="utf-8")

# Fix indentation around fits registration
# Let's clean up fits block
if 'from members.sota_baselines import' not in text:
    text = text.replace(
        'from members.amr_fbs import fit_amr_fbs, pred_amr_fbs',
        'from members.amr_fbs import fit_amr_fbs, pred_amr_fbs\nfrom members.sota_baselines import fit_dlinear, pred_dlinear, fit_fft, pred_fft, fit_theta, pred_theta'
    )

old_fits = """    fits["amr_fbs"] = (fit_amr_fbs, pred_amr_fbs)"""
new_fits = """    fits["amr_fbs"] = (fit_amr_fbs, pred_amr_fbs)
    fits["dlinear"] = (fit_dlinear, pred_dlinear)
    fits["spectral_fft"] = (fit_fft, pred_fft)
    fits["theta"] = (fit_theta, pred_theta)"""

if old_fits in text:
    text = text.replace(old_fits, new_fits)

p.write_text(text, encoding="utf-8")
print("Successfully fixed bench.py indentation and SOTA wiring.")
