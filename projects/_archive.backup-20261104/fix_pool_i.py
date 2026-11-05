import pathlib

path = pathlib.Path("bench.py")
text = path.read_text(encoding="utf-8")

# Remove accidental over-indented Pool I block and reinsert it at the correct level.
bad_prefix = "\n        poolI="
bad_end = "if _HAS_KNN and \"knn_forecaster\" in P_dict: out(f\"  Pool I (KNN Feature) {poolI} blend {maeI:.4f}\")\n"
start = text.find(bad_prefix)
if start >= 0:
    end = text.find(bad_end, start)
    if end < 0:
        raise RuntimeError("Could not find end of accidental Pool I block")
    end += len(bad_end)
    text = text[:start] + text[end:]

# Insert Pool I immediately after poolH assignment, at the same indentation.
marker = "poolH=poolA"
pos = text.find(marker)
if pos < 0:
    raise RuntimeError("Could not find poolH assignment")
insertion = '''        poolI=poolA+["knn_forecaster"] if _HAS_KNN else poolA
        poolI=[n for n in poolI if n in P_dict]
        maeI=pool_blend_mae(P_dict,A_ref,poolI) if "knn_forecaster" in P_dict else float("nan")
        if _HAS_KNN and "knn_forecaster" in P_dict: out(f"  Pool I (KNN Feature) {poolI} blend {maeI:.4f}")
'''
text = text[:pos] + insertion + text[pos:]
path.write_text(text, encoding="utf-8")
print("Fixed Pool I indentation")
