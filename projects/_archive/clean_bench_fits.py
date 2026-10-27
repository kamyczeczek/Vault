with open("bench.py", "r", encoding="utf-8") as f:
    text = f.read()

# Let's remove any bad insertions of sota baselines or amr_fbs and do it cleanly
if "from members.sota_baselines import" in text:
    # remove import
    text = text.replace("from members.sota_baselines import fit_dlinear, pred_dlinear, fit_theta, pred_theta, fit_fft, pred_fft\n", "")

# Let's add import at top or near other member imports
import_target = "from members.amr_fbs import fit_amr_fbs, pred_amr_fbs"
sota_import = import_target + "\nfrom members.sota_baselines import fit_dlinear, pred_dlinear, fit_theta, pred_theta, fit_fft, pred_fft"
text = text.replace(import_target, sota_import)

# Let's add fits cleanly
old_fits = """    if _HAS_BIGDICT:
        fits["bigdict_elm"] = (fit_bigdict, pred_bigdict)
        fits["amr_fbs"] = (fit_amr_fbs, pred_amr_fbs)"""

new_fits = """    if _HAS_BIGDICT:
        fits["bigdict_elm"] = (fit_bigdict, pred_bigdict)
        fits["amr_fbs"] = (fit_amr_fbs, pred_amr_fbs)
    fits["dlinear"] = (fit_dlinear, pred_dlinear)
    fits["theta_method"] = (fit_theta, pred_theta)
    fits["spectral_fft"] = (fit_fft, pred_fft)"""

# replace old_fits if present without duplicates
text = text.replace(old_fits, "")
text = text.replace('fits["bigdict_elm"] = (fit_bigdict, pred_bigdict)', new_fits)

with open("bench.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Cleaned and wired SOTA baselines into bench.py successfully.")
