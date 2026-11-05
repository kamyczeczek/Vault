import pathlib

path = pathlib.Path("bench.py")
text = path.read_text(encoding="utf-8")

# Ensure the import exists once.
if "_HAS_KNN" not in text:
    marker = '''    DeterministicCycleESN=None; _HAS_DETERMINISTIC_ESN=False
    print(f"DeterministicCycleESN unavailable: {_e}")'''
    insertion = marker + '''

try:
    from members.knn_feature_forecaster import KNNFeatureForecaster
    _HAS_KNN=True
except Exception as _e:
    KNNFeatureForecaster=None; _HAS_KNN=False
    print(f"KNNFeatureForecaster unavailable: {_e}")'''
    if marker not in text:
        raise RuntimeError("Could not find deterministic-ESN import marker")
    text = text.replace(marker, insertion, 1)

# Ensure fit/predict helpers exist once.
if "fit_knn_forecaster" not in text:
    marker = "def rolling_preds(series, H, fit_fn, pred_fn):"
    insertion = '''def fit_knn_forecaster(train, H):
    if not _HAS_KNN:
        raise RuntimeError("KNNFeatureForecaster unavailable")
    m = KNNFeatureForecaster(input_length=96, k_neighbors=24, alpha=10.0)
    m.fit(train, horizon=H)
    return m

def pred_knn_forecaster(model, hist):
    return model.predict_hist(hist)

'''
    if marker not in text:
        raise RuntimeError("Could not find rolling_preds marker")
    text = text.replace(marker, insertion + marker, 1)

# Ensure registration in the main fits dictionary.
if 'fits["knn_forecaster"]' not in text:
    marker = "    if _HAS_DETERMINISTIC_ESN:"
    insertion = '''    if _HAS_KNN:
        fits["knn_forecaster"] = (fit_knn_forecaster, pred_knn_forecaster)
'''
    if marker not in text:
        raise RuntimeError("Could not find fits registration marker")
    text = text.replace(marker, insertion + marker, 1)

# Ensure Pool I is reported after Pool H is defined.
if "Pool I (KNN Feature)" not in text:
    marker = "poolH=poolA"
    insertion = '''        poolI=poolA+["knn_forecaster"] if _HAS_KNN else poolA
        poolI=[n for n in poolI if n in P_dict]
        maeI=pool_blend_mae(P_dict,A_ref,poolI) if "knn_forecaster" in P_dict else float("nan")
        if _HAS_KNN and "knn_forecaster" in P_dict: out(f"  Pool I (KNN Feature) {poolI} blend {maeI:.4f}")
'''
    if marker not in text:
        raise RuntimeError("Could not find poolH marker")
    text = text.replace(marker, insertion + marker, 1)

path.write_text(text, encoding="utf-8")
print("KNN wiring complete")
