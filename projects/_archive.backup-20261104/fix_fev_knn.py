import pathlib

path = pathlib.Path("bench.py")
lines = path.read_text(encoding="utf-8").splitlines()

# Insert KNN into FEV fits_simple.
idx = next(i for i, line in enumerate(lines) if line.strip() == '"subband_d1": (fit_subbands, lambda m,h: pred_subband(m,h,"d1")),')
if not any('knn_forecaster' in line for line in lines[idx:idx+3]):
    lines.insert(idx + 1, '        "knn_forecaster": (fit_knn_forecaster, pred_knn_forecaster),')

# Insert FEV poolI immediately before poolB.
idx = next(i for i, line in enumerate(lines) if line.strip() == 'poolB=poolA+["subband_cA1","subband_d1"]')
if not any('poolI=poolA+["knn_forecaster"]' in line for line in lines[idx:idx+4]):
    lines.insert(idx, '        poolI=poolA+["knn_forecaster"] if _HAS_KNN else poolA')
    lines.insert(idx + 1, '        poolI=[n for n in poolI if n in P_dict]')

path.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("FEV KNN wiring complete")
