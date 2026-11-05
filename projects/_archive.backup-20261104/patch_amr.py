from pathlib import Path

# Patch bench.py
bench_path = Path("bench.py")
content = bench_path.read_text(encoding="utf-8")

import_block = "from members.big_dict_elm import fit_bigdict, pred_bigdict"
new_import = "from members.big_dict_elm import fit_bigdict, pred_bigdict\ntry:\n    from members.amr_fbs import fit_amr_fbs, pred_amr_fbs\n    _HAS_AMR = True\nexcept Exception:\n    _HAS_AMR = False"

if "amr_fbs" not in content:
    content = content.replace(import_block, new_import, 1)

    # Add wrapper functions
    wrapper = """
def fit_amr(train, H):
    if not _HAS_AMR: raise RuntimeError("amr_fbs unavailable")
    return fit_amr_fbs(train, H)

def pred_amr(model, hist):
    if not _HAS_AMR: raise RuntimeError("amr_fbs unavailable")
    return pred_amr_fbs(model, hist, len(model.W_) if hasattr(model, 'W_') else 24)
"""
    content += wrapper

    # Add to pool / registry in bench.py if needed
    # Let's add amr_fbs to pool members if present
    content = content.replace('"bigdict_elm"', '"bigdict_elm", "amr_fbs"')
    bench_path.write_text(content, encoding="utf-8")
    print("Patched bench.py successfully.")

# Patch sunspot_methods.py
sunspot_path = Path("sunspot_methods.py")
s_content = sunspot_path.read_text(encoding="utf-8")
if "amr_fbs" not in s_content:
    s_content = s_content.replace("fit_bigdict, pred_bigdict,", "fit_bigdict, pred_bigdict,\n                   fit_amr, pred_amr,")
    # add to get_sunspot_methods
    target = '"bigdict_elm": lambda train, hist, H: _direct(fit_bigdict, pred_bigdict, train, hist, H),'
    addition = '\n        "amr_fbs": lambda train, hist, H: _direct(fit_amr, pred_amr, train, hist, H),'
    s_content = s_content.replace(target, target + addition)
    sunspot_path.write_text(s_content, encoding="utf-8")
    print("Patched sunspot_methods.py successfully.")
