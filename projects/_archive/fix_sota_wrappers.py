from pathlib import Path

p = Path("members/sota_baselines.py")
text = p.read_text(encoding="utf-8")

# Update prediction wrappers to accept (model, hist)
old_wrappers = """def pred_dlinear(model, hist, H):
    return model.predict(hist, H)

def fit_fft(train, H):
    m = SpectralFFTBaseline()
    m.fit(train, H)
    return m

def pred_fft(model, hist, H):
    return model.predict(hist, H)

def fit_theta(train, H):
    m = ThetaBaseline()
    m.fit(train, H)
    return m

def pred_theta(model, hist, H):
    return model.predict(hist, H)"""

new_wrappers = """def pred_dlinear(model, hist):
    H = len(model.W_trend_.T) if model.W_trend_ is not None else 24
    return model.predict(hist, H)

def fit_fft(train, H):
    m = SpectralFFTBaseline()
    m.fit(train, H)
    return m

def pred_fft(model, hist):
    H = len(model.freqs_) * 5 if model.freqs_ is not None else 24
    return model.predict(hist, H)

def fit_theta(train, H):
    m = ThetaBaseline()
    m.fit(train, H)
    return m

def pred_theta(model, hist):
    return model.predict(hist, 24)"""

if "def pred_dlinear(model, hist, H):" in text:
    text = text.replace("def pred_dlinear(model, hist, H):", "def pred_dlinear(model, hist):")
    # let's update all three properly
    text = text.replace("def pred_fft(model, hist, H):", "def pred_fft(model, hist):")
    text = text.replace("def pred_theta(model, hist, H):", "def pred_theta(model, hist):")

p.write_text(text, encoding="utf-8")
print("Updated SOTA wrappers in members/sota_baselines.py successfully.")
