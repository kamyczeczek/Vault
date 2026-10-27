from pathlib import Path

p = Path("bench.py")
text = p.read_text(encoding="utf-8")

# Let's find where 'def main():' starts and replace the fits setup cleanly
if "def main():" in text:
    parts = text.split("def main():")
    header = parts[0]
    main_body = parts[1]

    # Reconstruct main fits initialization with 4-space indentation
    target_snippet = """    fits = {
        "nlinear_a1": (lambda tr, H: fit_nlinear(tr, H, 1.0), pred_nlinear),
        "nlinear_a10": (lambda tr, H: fit_nlinear(tr, H, 10.0), pred_nlinear),
        "rff_h64": (fit_rff, pred_rff),
        "subband_cA1": (fit_subbands, lambda m, h: pred_subband(m, h, "cA1")),
        "subband_d1": (fit_subbands, lambda m, h: pred_subband(m, h, "d1")),
    }
    if _HAS_ELM:
        fits["wavelet_pooled"] = (fit_pooled, pred_pooled)
    if _HAS_BIGDICT:
        fits["bigdict_elm"] = (fit_bigdict, pred_bigdict)
        fits["amr_fbs"] = (fit_amr_fbs, pred_amr_fbs)
        fits["dlinear"] = (fit_dlinear, pred_dlinear)
        fits["spectral_fft"] = (fit_fft, pred_fft)
        fits["theta"] = (fit_theta, pred_theta)"""

    # Replace old fits block in main_body
    # Let's find where 'fits = {' occurs in main_body
    idx_start = main_body.find('fits = {')
    if idx_start != -1:
        # find matching end of fits block or next if statement
        idx_end = main_body.find('if _HAS_BIGDICT_TREE:', idx_start)
        if idx_end != -1:
            main_body = main_body[:idx_start] + target_snippet + "\n    " + main_body[idx_end:]

    text = header + "def main():" + main_body

    # Ensure imports for amr_fbs and sota_baselines are at top of bench.py
    imports = "from members.amr_fbs import fit_amr_fbs, pred_amr_fbs\nfrom members.sota_baselines import fit_dlinear, pred_dlinear, fit_fft, pred_fft, fit_theta, pred_theta\n"
    if imports not in text:
        text = imports + text

    p.write_text(text, encoding="utf-8")
    print("Cleaned bench.py successfully with correct indentation.")
else:
    print("Could not find def main() in bench.py")
