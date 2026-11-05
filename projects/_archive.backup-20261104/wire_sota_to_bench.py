with open("bench.py", "r", encoding="utf-8") as f:
    text = f.read()

# Add import for sota baselines if not present
if "from members.sota_baselines import" not in text:
    import_target = "from members.amr_fbs import fit_amr_fbs, pred_amr_fbs"
    sota_import = import_target + "\nfrom members.sota_baselines import fit_dlinear, pred_dlinear, fit_theta, pred_theta, fit_fft, pred_fft"
    text = text.replace(import_target, sota_import)

# Add to fits dict
fits_target = 'if _HAS_BIGDICT:\n        fits["bigdict_elm"] = (fit_bigdict, pred_bigdict)\n        fits["amr_fbs"] = (fit_amr_fbs, pred_amr_fbs)'
sota_fits = fits_target + """
    fits["dlinear"] = (fit_dlinear, pred_dlinear)
    fits["theta_method"] = (fit_theta, pred_theta)
    fits["spectral_fft"] = (fit_fft, pred_fft)"""

if '"dlinear"' not in text:
    text = text.replace(fits_target, sota_fits)

with open("bench.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Successfully wired SOTA baselines into bench.py")
