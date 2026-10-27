"""BigDictTree — filter-bank + frozen nonlinear ELM dictionary + Decision Tree / ExtraTrees / GBDT readout, anchored (NLinear trick)."""
from __future__ import annotations
import numpy as np
from sklearn.tree import DecisionTreeRegressor, ExtraTreeRegressor
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor

try:
    import pywt
    _HAS_PYWT = True
except Exception:
    _HAS_PYWT = False

from members.big_dict_elm import _filter_bank_one

class BigDictTree:
    """Anchored feature bank + ELM random features -> Multi-Output Decision Tree Readout."""
    def __init__(
        self,
        input_length=96,
        hidden=128,  # tree doesn't need huge D; keeps training fast
        max_depth=6,
        min_samples_leaf=5,
        tree_type="decision_tree",  # 'decision_tree', 'extra_tree', 'extra_trees_ensemble', 'random_forest'
        n_estimators=20,
        wavelet_bank=("db4", "sym4"),
        levels=2,
        seed=42,
    ):
        self.input_length = int(input_length)
        self.hidden = int(hidden)
        self.max_depth = int(max_depth) if max_depth is not None else None
        self.min_samples_leaf = int(min_samples_leaf)
        self.tree_type = tree_type
        self.n_estimators = int(n_estimators)
        self.wavelet_bank = wavelet_bank
        self.levels = int(levels)
        self.seed = int(seed)
        self._fitted = False

    def _bank(self, xa):
        return _filter_bank_one(
            xa,
            wavelet_bank=self.wavelet_bank,
            levels=self.levels,
            use_packet=False,
            packet_depth=2,
        )

    def _build_tree(self):
        if self.tree_type in ("tree", "decision_tree", "dt"):
            return DecisionTreeRegressor(
                max_depth=self.max_depth,
                min_samples_leaf=self.min_samples_leaf,
                random_state=self.seed,
            )
        elif self.tree_type == "extra_tree":
            return ExtraTreeRegressor(
                max_depth=self.max_depth,
                min_samples_leaf=self.min_samples_leaf,
                random_state=self.seed,
            )
        elif self.tree_type == "extra_trees_ensemble":
            return ExtraTreesRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                min_samples_leaf=self.min_samples_leaf,
                n_jobs=-1,
                random_state=self.seed,
            )
        elif self.tree_type == "random_forest":
            return RandomForestRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                min_samples_leaf=self.min_samples_leaf,
                n_jobs=-1,
                random_state=self.seed,
            )
        else:
            raise ValueError(f"Unknown tree_type: {self.tree_type}")

    def fit(self, y, *, horizon: int):
        series = np.asarray(y, dtype=float).ravel()
        L = self.input_length
        H = int(horizon)
        n = len(series)
        if n < L + H:
            raise ValueError(f"series too short {n} < {L+H}")

        ends = np.arange(L, n - H + 1)
        flats = []
        deltas = []
        for e in ends:
            w = series[e - L:e]
            a = float(w[-1])
            xa = w - a
            flat = np.concatenate(self._bank(xa)).astype(float)
            flats.append(flat)
            tgt = series[e:e + H] - a
            deltas.append(tgt)

        X0 = np.stack(flats, axis=0)
        Y = np.stack(deltas, axis=0)

        # Standardise features
        self.mu_ = X0.mean(axis=0)
        sd = X0.std(axis=0)
        sd[sd < 1e-8] = 1.0
        self.sd_ = sd
        Xs = (X0 - self.mu_) / self.sd_
        D0 = Xs.shape[1]

        # ELM Random non-linear projections
        if self.hidden > 0:
            rng = np.random.default_rng(self.seed)
            scale = 1.0 / np.sqrt(D0)
            Wr = rng.standard_normal((D0, self.hidden)) * scale
            b = rng.uniform(0, 2 * np.pi, size=self.hidden)
            phi_rand = np.cos(Xs @ Wr + b)
            # Sample non-linear squared features
            stride = max(1, D0 // 32)
            idx = np.arange(0, D0, stride)[:32]
            phi_sq = Xs[:, idx] ** 2
            Phi = np.concatenate([Xs, phi_rand, phi_sq], axis=1)
            self.Wr_ = Wr
            self.b_ = b
            self.idx_ = idx
        else:
            Phi = Xs

        self.D0_ = D0
        self.Phi_dim_ = Phi.shape[1]

        # Fit multi-output Decision Tree on deltas (Y is n_samples x H)
        tree = self._build_tree()
        tree.fit(Phi, Y)
        self.tree_ = tree
        self.H_ = H
        self.history_ = series
        self._fitted = True
        return self

    def _phi_for_hist(self, hist):
        hist = np.asarray(hist, dtype=float).ravel()
        L = self.input_length
        if len(hist) < L:
            hist = np.pad(hist, (L - len(hist), 0), mode="edge")
        else:
            hist = hist[-L:]
        a = float(hist[-1])
        xa = hist - a
        flat = np.concatenate(self._bank(xa)).astype(float)
        Xs = (flat - self.mu_) / self.sd_
        if self.hidden > 0:
            phi_rand = np.cos(Xs @ self.Wr_ + self.b_)
            phi_sq = Xs[self.idx_] ** 2
            Phi = np.concatenate([Xs, phi_rand, phi_sq], axis=0)
        else:
            Phi = Xs
        return Phi, a

    def predict_hist(self, hist):
        if not self._fitted:
            raise RuntimeError("fit first")
        Phi, a = self._phi_for_hist(hist)
        delta = self.tree_.predict(Phi[None, :])[0]
        return delta + a

    def predict(self):
        return self.predict_hist(self.history_[-self.input_length:])
