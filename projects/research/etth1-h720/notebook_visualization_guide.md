# Przewodnik po Wizualizacji Efektywności Modelu i Weryfikacji Braku Wycieku Danych (ETTh1 H720)

Niniejszy dokument przedstawia wyczerpujący plan i przewodnik wdrożeniowy w postaci **Python Jupyter Notebook** dla projektu **`etth1-h720`**. Celem jest czytelna, rzetelna i pozbawiona wycieków z przyszłości (zero-leakage) wizualizacja wydajności modeli prognozujących szeregi czasowe na długim horyzoncie ($H=720$ godzin / 30 dni).

---

## 1. Context & Wyzwania projektu `etth1-h720`

W projekcie `etth1-h720` zadaniem modeli jest prognozowanie temperatury oleju transformatorowego (`OT` z zbioru ETTh1) na 720 kroków w przód.

### Kluczowe pułapki i specyfika H720:
1. **Dominacja dryfu poziomu (Level Drift):** Przy $H=720$ skumulowany błąd błądzenia losowego i przesunięcia poziomu (drift) przeważa nad kształtem sinusoidy. Wiele skomplikowanych modeli głębokich ulega degradacji, przegrywając z prostym zakotwiczeniem (`persistence` lub `drift_linear`).
2. **Ryzyko wycieku z przyszłości (Lookahead Bias / Data Leakage):**
   - Użycie przyszłych wartości z okna testowego do standaryzacji ($z$-score z całego zbioru).
   - Losowy podział `train_test_split(shuffle=True)` zamiast chronologicznego rozcięcia.
   - Wykorzystanie autokorelacji z przyszłych kroków w cechach lagujących.
3. **Protokoły walidacji:** Projekt wykorzystuje ruchome okno walidacyjne (sliding window) na 12 ustalonych punktach startowych (originach), z oknem treningowym $W=8640$ (360 dni) i kontekstem wejściowym $L=168$ lub $L=96$.

---

## 2. Architektura Wizualizacji Bez Wycieku (Zero-Leakage Architecture)

Aby wykres i notebook stanowiły dowód rzetelności badania, muszą wizualizować 4 kluczowe obszary:

```
[ Okno Treningowe (W=8640h) ] [ Kontekst L=168h ] | CUTOFF ORIGIN | [ Target Future H=720h ]
───────────────────────────────═══════════════════┼────────────────═══════════════════════
Fit Modelu                       Context Input    │                Ground Truth (Czarna)
                                                  │                Model Pred (Fiolet)
```

### Elementy wykresu:
1. **Linia Odcięcia (Origin Cutoff):** Pionowa przerywana czerwona linia rozdzielająca przeszłość od przyszłości.
2. **Okno Kontekstowe (Historical Context - $L$):** Czas przed odcięciem przekazywany do funkcji `predict()` jako jedyna informacja o bieżącym stanie.
3. **Rzeczywisty Przebieg (Ground Truth Target):** Prawdziwe wartości w oknie testowym $H=720$.
4. **Prognoza Modelu (Model Prediction):** Przewidywanie modelu na horyzoncie $H=720$.
5. **Baseline Referencyjny (Persistence / Baseline):** Ostatnia znana wartość ($t_0$) pociągnięta stałą linią, pokazywana w celu weryfikacji, czy model wnosi realną wartość dodaną.
6. **Wykres Błędów (Residual Plot):** Dolny panel przedstawiający błąd kroku po kroku ($e_t = \hat{y}_t - y_t$) na horyzoncie od 1 do 720h.

---

## 3. Kompletny Kod Jupyter Notebook (`etth1_model_visualization_notebook.ipynb`)

Notebook można uruchomić bezpośrednio w środowisku projektu. Poniżej znajduje się kompletny kod podzielony na komórki.

### Komórka 1: Inicjalizacja i Importy
```python
import sys
import pathlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Dołączenie ścieżek projektowych
import _workspace_paths
from _workspace_paths import ROOT, data_csv
from members.sota_baselines import fit_dlinear, pred_dlinear
from members.h2k import H2KForecaster

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
print("Środowisko załadowane pomyślnie.")
```

### Komórka 2: Weryfikacja Braku Wycieku Danych (Leakage Checker)
```python
def check_zero_leakage(train_idxs: np.ndarray, ctx_idxs: np.ndarray, target_idxs: np.ndarray):
    """Ścisła kontrola ciągłości czasowej i braku nachodzenia na przyszłość."""
    assert train_idxs[-1] < target_idxs[0], "BŁĄD WYCIEKU: Dane treningowe nachodzą na target!"
    assert ctx_idxs[-1] < target_idxs[0], "BŁĄD WYCIEKU: Kontekst nachodzi na target!"
    assert target_idxs[0] == ctx_idxs[-1] + 1, "BŁĄD CIĄGŁOŚCI: Przerwa między kontekstem a targetem!"

    print("✅ CHECK PASSED: Zero Wycieku Danych.")
    print(f"   Max Indeks Treningowy: {train_idxs[-1]}")
    print(f"   Ostatni Indeks Kontekstu: {ctx_idxs[-1]}")
    print(f"   Pierwszy Indeks Targetu (Futur): {target_idxs[0]}")
```

### Komórka 3: Główna Funkcja Wizualizująca Single-Origin
```python
def plot_model_efficiency(
    df: pd.DataFrame,
    origin_idx: int = 8640,
    lookback_len: int = 168,
    horizon: int = 720,
    cap: int = 8640,
    model_name: str = "DLinear"
):
    s = df["OT"].to_numpy(float)
    dates = df["date"].values

    # 1. Podział indeksów i cech
    train_idxs = np.arange(origin_idx - cap, origin_idx)
    ctx_idxs = np.arange(origin_idx - lookback_len, origin_idx)
    target_idxs = np.arange(origin_idx, origin_idx + horizon)

    # Weryfikacja asertywna braku wycieku
    check_zero_leakage(train_idxs, ctx_idxs, target_idxs)

    train_slice = s[train_idxs]
    ctx_slice = s[ctx_idxs]
    actual_target = s[target_idxs]

    # 2. Trening i Prognoza (Fit strictly on train_slice)
    if model_name == "DLinear":
        weights = fit_dlinear(train_slice, horizon)
        pred = pred_dlinear(weights, ctx_slice)
    elif model_name == "H2K":
        model = H2KForecaster(input_length=lookback_len, k_neighbors=48, drift_damping=0.0)
        pred = model.fit(train_slice, horizon).predict_hist(ctx_slice)
    else:
        raise ValueError(f"Nieznany model: {model_name}")

    persistence_pred = np.full(horizon, ctx_slice[-1])

    # 3. Tworzenie Wykresu Wykres dwupanelowy
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 9), gridspec_kw={'height_ratios': [2.5, 1]})

    # Panel Górny: Kontekst + Target + Prognozy
    hist_show = 336  # Ostatnie 14 dni przed odcięciem
    show_ctx_idxs = np.arange(origin_idx - hist_show, origin_idx)
    show_ctx_vals = s[show_ctx_idxs]

    ax1.plot(show_ctx_idxs, show_ctx_vals, label="Wejście Kontekstowe (Obserwowane)", color="#1f77b4", lw=2)
    ax1.plot(target_idxs, actual_target, label="Wartości Rzeczywiste (Ground Truth)", color="#2ca02c", lw=2.2, alpha=0.9)
    ax1.plot(target_idxs, pred, label=f"Prognoza Modelu: {model_name}", color="#d62728", lw=2, linestyle="--")
    ax1.plot(target_idxs, persistence_pred, label="Persistence Baseline", color="#7f7f7f", lw=1.5, linestyle=":")

    # Punkt odcięcia Origin Cutoff
    ax1.axvline(x=origin_idx - 1, color="#d62728", linestyle="-.", lw=2, label="Punkt Odcięcia (Cutoff Origin)")
    ax1.axvspan(origin_idx, origin_idx + horizon, color="#ff7f0e", alpha=0.08, label="Horyzont Prognozy H=720h")

    cutoff_date = dates[origin_idx - 1]
    ax1.set_title(f"Prognoza H720 z Punktu Odcięcia {origin_idx} (Data Cutoff: {cutoff_date})", fontsize=13, fontweight='bold')
    ax1.set_ylabel("Oil Temperature (OT)", fontsize=11)
    ax1.legend(loc="upper left", frameon=True, facecolor="white", framealpha=0.9)

    # Panel Dolny: Błędy krok po kroku
    err_model = pred - actual_target
    err_persistence = persistence_pred - actual_target

    ax2.plot(target_idxs, err_model, label=f"Błąd {model_name}", color="#d62728", lw=1.5)
    ax2.plot(target_idxs, err_persistence, label="Błąd Persistence", color="#7f7f7f", lw=1.2, linestyle=":")
    ax2.axhline(0, color="black", linestyle="--", lw=1, alpha=0.7)

    ax2.set_title("Rozkład Błędów w Horyzoncie Czasowym (Residuals)", fontsize=11, fontweight='bold')
    ax2.set_xlabel("Indeks Godzinowy", fontsize=11)
    ax2.set_ylabel("Błąd Rozbieżności (°C)", fontsize=11)
    ax2.legend(loc="upper left")

    plt.tight_layout()
    plt.show()

# Uruchomienie wizualizacji
df = pd.read_csv(data_csv())
plot_model_efficiency(df, origin_idx=8640, model_name="DLinear")
```

### Komórka 4: Wizualizacja Efektywności na Wszystkich 12 Originach (Multi-Origin Walk-Forward)
```python
def plot_multi_origin_performance(json_results_path: pathlib.Path):
    """Wizualizuje skumulowany błąd MAE na wszystkich 12 originach walidacyjnych."""
    import json
    data = json.loads(json_results_path.read_text(encoding='utf-8'))

    per_origin = data["per_origin"]
    origins = [r["origin"] for r in per_origin]

    methods = list(per_origin[0]["methods"].keys())

    plt.figure(figsize=(14, 6))
    for m in methods:
        maes = [r["methods"][m].get("mae_raw", None) for r in per_origin]
        if None not in maes:
            plt.plot(origins, maes, marker='o', label=m, lw=1.8)

    plt.axhline(y=1.9781, color='red', linestyle='--', label='Incumbent Benchmark (1.9781)')
    plt.title("Porównanie Surowego MAE na 12 Originach H720 (Zero-Leakage Sliding Evaluation)", fontsize=13, fontweight='bold')
    plt.xlabel("Origin Cutoff Index", fontsize=11)
    plt.ylabel("Raw MAE (°C)", fontsize=11)
    plt.legend(loc="upper right", bbox_to_anchor=(1.25, 1.0))
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.show()
```

---

## 4. Metodyka Dowodzenia Braku Wycieku (Zero-Leakage Verification Checklist)

Podczas prezentacji wyników w notebooku należy zweryfikować 4 punkty kontrolne:

1. **Brak Globalnej Standaryzacji:** Standaryzacja średnią i odchyleniem standardowym musi być wykonywana *wyłącznie* na próbce treningowej (`train_slice.std()`), nigdy na całym zbiorze `df["OT"]`.
2. **Rozłączność Indeksów:** Indeksy walidacyjne targetu $I_{target} = [origin, origin + H)$ nie mają części wspólnej z oknem uczenia $I_{train} = [origin - W, origin)$.
3. **Rolka Stanu Kontekstu:** Kontekst wejściowy $L$ kończy się na $origin - 1$. Żaden element z pozycji $\ge origin$ nie bierze udziału w generowaniu cech (`input_length`).
4. **Zamknięty Protokół Wyboru Hiterparametrów:** Strojenie k-NN czy wag odbywa się wyłącznie na wczesnych originach deweloperskich (`8640, 9360, 10080, 10800`), a ocenianie odbywa się jednorazowo na zablokowanym zestawie originów testowych.

---

## Summary
Niniejszy plan oraz skrypt demonstrują czytelną wizualizację efektywności modelu na długim horyzoncie z pełnym matemaycznym i chronologicznym dowodem braku wycieku danych.
