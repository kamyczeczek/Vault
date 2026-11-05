"""S-45 — new blend members (D1/D3): 7-channel cross-attention PatchTST + seed-1 twin.

Pre-registration contract: S45_DESIGN.md in this directory (D1, D3) — FINAL and
BINDING; implemented verbatim.

Member 1: patchtst_P24_D32_2L_s1 — PatchTSTModelS1, a ONE-DELTA mirror of Bet 3's
PatchTSTModel.fit. The ONLY change vs
patchtst_delta_bet3/patchtst_encoder.py::PatchTSTModel.fit is the determinism
call at fit() start:

    Bet 3:  _set_deterministic()          # module-level seed 0
    S-45:   _set_deterministic_seed(1)    # this module, seed 1

Why a mirror rather than an external pre-seed: the parent fit() re-seeds to 0
internally at its start, which would overwrite any external seed — the seed MUST
be parameterized at that call site (S45_DESIGN.md D1). The call happens BEFORE
PatchTSTDelta construction and every torch.randperm, so weight init AND batch
order both derive from seed 1 — a genuinely independent draw. Everything else
below (mu/sigma, dataset, architecture, optimizer, early stop patience 40 /
max_epochs 400, best-state restore, diagnostics) is line-for-line Bet 3's fit().

Member 2: patchtst_cross_P24_D32_2L — 7-channel level-free cross-attention
PatchTST (D3): 98 tokens channel-major (t = c*14 + p), per-channel level-free
shift (W - W[335], broadcast per channel), channel-shared linear patch
projection P24 -> D32 + learnable positional encoding (per patch position,
R^{14x32}) + learnable channel embedding (R^{7x32}), 2-layer Transformer
(heads=2, FFN=64, dropout 0.30, stochastic depth 0.10, attn-dropout 0.2, NO
causal mask — bidirectional attention lets tokens attend ACROSS channels, the
non-linear cross-channel interaction Bet 2's close demands, on the exogenous
inputs Bet 3's close demands), decoder = pooled token mean -> per-horizon linear
head -> R^720 OT delta + OT anchor re-add. Train-only
per-channel-per-patch-position-per-element mu/sigma (R^{7x14x24}, recomputed per
phase from that phase's training series only — Bet 2 patch_embed train-only
discipline). Target is OT-only; multivariate information enters ONLY through
inputs. Seed 0 (D3).
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "patchtst_delta_bet3"))

from patchtst_encoder import PatchTSTDelta, PatchTSTModel, _StochasticDepth, ffn_for  # noqa: E402


def _set_deterministic_seed(seed: int):
    """Parameterized mirror of patchtst_encoder._set_deterministic (D1)."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


# =====================================================================
# Member 1: the seed-1 twin (D1)
# =====================================================================
class PatchTSTModelS1(PatchTSTModel):
    """Seed-1 twin of the univariate PatchTST-Delta member (S45_DESIGN.md D1).

    ONE-DELTA mirror of patchtst_encoder.py::PatchTSTModel.fit — the ONLY
    change is the determinism call at fit() start (see module docstring).
    All other methods (_make_tokens, _build_dataset, predict,
    _attention_entropy) are inherited VERBATIM from Bet 3's PatchTSTModel.
    """

    def fit(self, y, *, horizon: int, target_index: int = 0) -> "PatchTSTModelS1":
        series = np.asarray(y, dtype=float)
        if series.ndim == 2:
            series = series[:, target_index]
        _set_deterministic_seed(1)  # ONLY DELTA vs PatchTSTModel.fit (D1):
        #                            Bet 3 calls the module-level
        #                            _set_deterministic() (seed 0) at this
        #                            exact call site; the twin re-seeds to 1.
        L = 336
        # train-only patch statistics over shifted windows
        # compute mu/sigma via a quick pass mirroring patch_embed semantics
        shifts = []
        n_tokens = L // self.patch_size
        for end in range(L, len(series) - self.H + 1):
            w = series[end - L:end]
            shifted = (w - w[-1])[: n_tokens * self.patch_size].reshape(n_tokens, self.patch_size)
            shifts.append(shifted)
        shifts = np.stack(shifts, axis=0)  # (N, n_tokens, P)
        self.mu = shifts.mean(axis=(0, 1)).astype(np.float32)
        self.sigma = np.maximum(shifts.std(axis=(0, 1)), 1e-6).astype(np.float32)

        self.history_ = series
        self.horizon_ = horizon
        self.target_index = target_index

        X, Y, _ = self._build_dataset(series)
        n = X.shape[0]
        n_val = max(1, n // 8)
        X_tr, Y_tr = X[:-n_val], Y[:-n_val]
        X_va, Y_va = X[-n_val:], Y[-n_val:]

        self.net = PatchTSTDelta(
            P=self.patch_size, D=self.D, n_layers=self.n_layers, n_heads=2,
            ffn=ffn_for(self.patch_size, self.D), H=horizon,
            dropout=0.30, attn_dropout=0.2, stochastic_depth=0.10,
        ).to(self.device)
        self.optimizer = torch.optim.AdamW(self.net.param_groups, lr=self.lr)

        X_tr_d = X_tr.to(self.device)
        Y_tr_d = Y_tr.to(self.device)
        X_va_d = X_va.to(self.device)
        Y_va_d = Y_va.to(self.device)

        best_val = float("inf")
        best_state = None
        epochs_no_improve = 0
        scaler = torch.cuda.amp.GradScaler(enabled=self.amp and self.device != "cpu")

        for epoch in range(self.max_epochs):
            self.net.train()
            perm = torch.randperm(X_tr_d.shape[0])
            total = 0.0
            nbat = 0
            for s in range(0, X_tr_d.shape[0], self.batch):
                idx = perm[s:s + self.batch]
                xb, yb = X_tr_d[idx], Y_tr_d[idx]
                self.optimizer.zero_grad()
                if self.amp and self.device != "cpu":
                    with torch.cuda.amp.autocast():
                        pred = self.net(xb)
                        loss = torch.mean(torch.abs(pred - yb))
                    scaler.scale(loss).backward()
                    scaler.unscale_(self.optimizer)
                    torch.nn.utils.clip_grad_norm_(self.net.parameters(), self.grad_clip)
                    scaler.step(self.optimizer)
                    scaler.update()
                else:
                    pred = self.net(xb)
                    loss = torch.mean(torch.abs(pred - yb))
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(self.net.parameters(), self.grad_clip)
                    self.optimizer.step()
                total += float(loss.item()) * xb.shape[0]
                nbat += xb.shape[0]
            train_mae = total / max(1, nbat)

            self.net.eval()
            with torch.no_grad():
                vp = self.net(X_va_d)
                val_mae = float(torch.mean(torch.abs(vp - Y_va_d)).item())
                # attention entropy diagnostic (mean over heads/tokens of attn map)
                try:
                    ent = self._attention_entropy(X_va_d[:1])
                except Exception:
                    ent = float("nan")
            self.attention_entropies_.append(ent)

            gap = train_mae - val_mae
            if epoch % 5 == 0 or val_mae < best_val:
                print(f"    [PatchTST P{self.patch_size} D{self.D} L{self.n_layers}] "
                      f"ep {epoch:3d} train {train_mae:.4f} val {val_mae:.4f} gap {gap:+.4f} ent {ent:.3f}")
            if val_mae < best_val - 1e-6:
                best_val = val_mae
                best_state = copy.deepcopy(self.net.state_dict())
                epochs_no_improve = 0
            else:
                epochs_no_improve += 1
                if epochs_no_improve >= self.patience:
                    print(f"    early stop ep {epoch} best_val {best_val:.4f}")
                    break

        if best_state is not None:
            self.net.load_state_dict(best_state)
        self.best_val_delta_mae_ = best_val
        self.train_val_gap_ = train_mae - best_val
        self.net.eval()
        return self


# =====================================================================
# Member 2: the 7-channel cross-attention PatchTST (D3)
# =====================================================================
CROSS_L = 336
CROSS_CHANNELS = 7           # CHANNELS order: [OT, HUFL, HULL, MUFL, MULL, LUFL, LULL]
CROSS_N_PATCHES = 14         # 336 // 24
CROSS_N_TOKENS = 98         # 7 * 14, channel-major t = c*14 + p


class PatchTSTCrossDelta(nn.Module):
    """7-channel cross-attention PatchTST-Delta forecaster (S45_DESIGN.md D3).

    input  : X (N, 98, 24) raw per-channel patch tokens (t = c*14 + p)
    output : OT delta forecast (N, H)
    """

    def __init__(self, P: int = 24, D: int = 32, n_layers: int = 2, n_heads: int = 2,
                 ffn: int = 64, H: int = 720,
                 dropout: float = 0.30, attn_dropout: float = 0.2,
                 stochastic_depth: float = 0.10):
        super().__init__()
        assert D % n_heads == 0, "D must be divisible by n_heads"
        self.P, self.D, self.H = P, D, H

        self.proj = nn.Linear(P, D)                              # channel-shared token projection
        self.pos = nn.Parameter(torch.zeros(1, CROSS_N_PATCHES, D))   # per patch position
        self.ch = nn.Parameter(torch.zeros(1, CROSS_CHANNELS, D))     # learnable channel embedding
        self.drop = nn.Dropout(dropout)

        layer = nn.TransformerEncoderLayer(
            d_model=D, nhead=n_heads, dim_feedforward=ffn,
            dropout=dropout, activation="gelu", batch_first=True,
            norm_first=True,
        )
        layer.self_attn.dropout = attn_dropout
        self.encoder = nn.TransformerEncoder(layer, num_layers=n_layers)

        self.stoch = nn.ModuleList([_StochasticDepth(stochastic_depth)
                                    for _ in range(n_layers)])
        self.head = nn.Linear(D, H)  # per-horizon linear head (non-norm)

        # token index tables: t = c*14 + p (channel-major, D3)
        self.register_buffer("p_idx", torch.arange(CROSS_N_TOKENS) % CROSS_N_PATCHES,
                             persistent=False)
        self.register_buffer("c_idx", torch.arange(CROSS_N_TOKENS) // CROSS_N_PATCHES,
                             persistent=False)
        self._build_param_groups()

    def _build_param_groups(self):
        # weight decay grouping mirrors Bet 3: decay proj+head; none on norms, pos, ch
        decay, no_decay = [], []
        for name, p in self.named_parameters():
            if not p.requires_grad:
                continue
            if "norm" in name or name in ("pos", "ch"):
                no_decay.append(p)
            else:
                decay.append(p)
        self.param_groups = [
            {"params": decay, "weight_decay": 1e-2},
            {"params": no_decay, "weight_decay": 0.0},
        ]

    def forward(self, X: torch.Tensor) -> torch.Tensor:
        # X: (N, 98, P) -> OT delta pred (N, H); NO causal mask (bidirectional,
        # cross-channel attention — the D3 licensing mechanism)
        h = self.proj(X) + self.pos[:, self.p_idx, :] + self.ch[:, self.c_idx, :]
        h = self.drop(h)
        h = self.encoder(h)
        for sd in self.stoch:
            h = sd(h)
        pooled = h.mean(dim=1)
        return self.head(pooled)

    def count_params(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


class PatchTSTCrossModel:
    """Fit/predict wrapper for the cross member (multivariate series, OT target).

    fit(y, *, horizon) with y an (N, 7) series in CHANNELS order
    [OT, HUFL, HULL, MUFL, MULL, LUFL, LULL] (D3 data path; OT is channel 0).
    The target delta is OT-only — multivariate information enters ONLY through
    inputs. predict() uses self.history_ (the (N,7) series passed to fit),
    mirroring the Bet 3 member contract (history swap for rolling origins).
    """

    def __init__(self, patch_size: int = 24, D: int = 32, n_layers: int = 2,
                 n_heads: int = 2, ffn: int = 64, H: int = 720,
                 dropout: float = 0.30, attn_dropout: float = 0.2,
                 stochastic_depth: float = 0.10,
                 lr: float = 3e-4, batch: int = 64, grad_clip: float = 1.0,
                 max_epochs: int = 400, patience: int = 40,
                 device: str = "cpu", amp: bool = False):
        self.patch_size = patch_size
        self.D = D
        self.n_layers = n_layers
        self.n_heads = n_heads
        self.H = H
        self.lr = lr
        self.batch = batch
        self.grad_clip = grad_clip
        self.max_epochs = max_epochs
        self.patience = patience
        self.device = device
        self.amp = amp
        self.mu = None
        self.sigma = None
        self.history_ = None
        self.horizon_ = H
        self.attention_entropies_ = []
        self.train_val_gap_ = None

    # ----- tokenization (level-free per channel, train-only standardized) -----
    def _make_tokens(self, window: np.ndarray) -> np.ndarray:
        """window: (336, 7) -> (98, 24) standardized tokens, t = c*14 + p.

        Level-free per channel: subtract each channel's own window[-1]
        (broadcast, D3). Standardize with train-only per-(channel, patch,
        position) mu/sigma laid out identically (7, 14, 24) -> (98, 24).
        """
        anchor = window[-1]                     # (7,) per-channel last value
        shifted = window - anchor               # broadcast per channel
        # (336, 7) -> (14, 24, 7) -> transpose -> (7, 14, 24) -> (98, 24)
        v = shifted.reshape(CROSS_N_PATCHES, self.patch_size, CROSS_CHANNELS)
        v = v.transpose(2, 0, 1).reshape(CROSS_N_TOKENS, self.patch_size)
        # mu/sigma stored (7, 14, 24); reshape to the SAME channel-major token
        # layout t = c*14 + p -> (98, 24)
        mu_t = self.mu.reshape(CROSS_CHANNELS * CROSS_N_PATCHES, self.patch_size)
        sigma_t = self.sigma.reshape(CROSS_CHANNELS * CROSS_N_PATCHES, self.patch_size)
        v = (v - mu_t) / sigma_t
        return v.astype(np.float32)

    def _channel_stats(self, series: np.ndarray):
        """Train-only per-(channel, patch, position) mu/sigma over level-free
        shifted windows — Bet 2 patch_embed train-only discipline (D3), extended
        per channel. Uses the SAME window set as the training dataset (mirror
        of Bet 3's fit() stats pass)."""
        ends = range(CROSS_L, len(series) - self.H + 1)
        stack = np.empty((len(ends), CROSS_L, CROSS_CHANNELS), dtype=np.float32)
        for i, end in enumerate(ends):
            w = series[end - CROSS_L:end]
            stack[i] = (w - w[-1]).astype(np.float32)
        # (N, 14, 24, 7) -> (N, 7, 14, 24); stats over windows (axis 0)
        v = stack.reshape(len(ends), CROSS_N_PATCHES, self.patch_size, CROSS_CHANNELS)
        v = v.transpose(0, 3, 1, 2)
        mu = v.mean(axis=0, dtype=np.float64)
        sigma = np.maximum(v.std(axis=0, dtype=np.float64), 1e-6)
        return mu.astype(np.float32), sigma.astype(np.float32)

    def _build_dataset(self, series: np.ndarray):
        Xs, Ys = [], []
        for end in range(CROSS_L, len(series) - self.H + 1):
            window = series[end - CROSS_L:end]              # (336, 7)
            tokens = self._make_tokens(window)              # (98, 24)
            ot_anchor = window[-1, 0]                       # OT last value
            target = series[end:end + self.H, 0] - ot_anchor  # OT-only delta
            Xs.append(tokens)
            Ys.append(target.astype(np.float32))
        X = torch.tensor(np.stack(Xs), dtype=torch.float32)
        Y = torch.tensor(np.stack(Ys), dtype=torch.float32)
        return X, Y

    def fit(self, y, *, horizon: int) -> "PatchTSTCrossModel":
        series = np.asarray(y, dtype=float)
        assert series.ndim == 2 and series.shape[1] == CROSS_CHANNELS, \
            f"cross member needs an (N, {CROSS_CHANNELS}) series, got {series.shape}"
        _set_deterministic_seed(0)  # D3: the cross member trains under seed 0

        self.mu, self.sigma = self._channel_stats(series)
        self.history_ = series
        self.horizon_ = horizon

        X, Y = self._build_dataset(series)
        n = X.shape[0]
        n_val = max(1, n // 8)
        X_tr, Y_tr = X[:-n_val], Y[:-n_val]
        X_va, Y_va = X[-n_val:], Y[-n_val:]

        self.net = PatchTSTCrossDelta(
            P=self.patch_size, D=self.D, n_layers=self.n_layers,
            n_heads=self.n_heads, ffn=ffn_for(self.patch_size, self.D), H=horizon,
            dropout=0.30, attn_dropout=0.2, stochastic_depth=0.10,
        ).to(self.device)
        self.optimizer = torch.optim.AdamW(self.net.param_groups, lr=self.lr)

        X_tr_d = X_tr.to(self.device)
        Y_tr_d = Y_tr.to(self.device)
        X_va_d = X_va.to(self.device)
        Y_va_d = Y_va.to(self.device)

        best_val = float("inf")
        best_state = None
        epochs_no_improve = 0
        scaler = torch.cuda.amp.GradScaler(enabled=self.amp and self.device != "cpu")

        for epoch in range(self.max_epochs):
            self.net.train()
            perm = torch.randperm(X_tr_d.shape[0])
            total = 0.0
            nbat = 0
            for s in range(0, X_tr_d.shape[0], self.batch):
                idx = perm[s:s + self.batch]
                xb, yb = X_tr_d[idx], Y_tr_d[idx]
                self.optimizer.zero_grad()
                if self.amp and self.device != "cpu":
                    with torch.cuda.amp.autocast():
                        pred = self.net(xb)
                        loss = torch.mean(torch.abs(pred - yb))
                    scaler.scale(loss).backward()
                    scaler.unscale_(self.optimizer)
                    torch.nn.utils.clip_grad_norm_(self.net.parameters(), self.grad_clip)
                    scaler.step(self.optimizer)
                    scaler.update()
                else:
                    pred = self.net(xb)
                    loss = torch.mean(torch.abs(pred - yb))
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(self.net.parameters(), self.grad_clip)
                    self.optimizer.step()
                total += float(loss.item()) * xb.shape[0]
                nbat += xb.shape[0]
            train_mae = total / max(1, nbat)

            self.net.eval()
            with torch.no_grad():
                vp = self.net(X_va_d)
                val_mae = float(torch.mean(torch.abs(vp - Y_va_d)).item())
                try:
                    ent = self._attention_entropy(X_va_d[:1])
                except Exception:
                    ent = float("nan")
            self.attention_entropies_.append(ent)

            gap = train_mae - val_mae
            if epoch % 5 == 0 or val_mae < best_val:
                print(f"    [PatchTST-cross P{self.patch_size} D{self.D} L{self.n_layers}] "
                      f"ep {epoch:3d} train {train_mae:.4f} val {val_mae:.4f} gap {gap:+.4f} ent {ent:.3f}")
            if val_mae < best_val - 1e-6:
                best_val = val_mae
                best_state = copy.deepcopy(self.net.state_dict())
                epochs_no_improve = 0
            else:
                epochs_no_improve += 1
                if epochs_no_improve >= self.patience:
                    print(f"    early stop ep {epoch} best_val {best_val:.4f}")
                    break

        if best_state is not None:
            self.net.load_state_dict(best_state)
        self.best_val_delta_mae_ = best_val
        self.train_val_gap_ = train_mae - best_val
        self.net.eval()
        return self

    def _attention_entropy(self, xb: torch.Tensor) -> float:
        # attention entropy (nats) of the first encoder layer, averaged over
        # heads/tokens — mirror of Bet 3's diagnostic, with the token tables.
        # Uniform-attention ceiling ln(98) ~ 4.58 (vs ln(14) ~ 2.64 univariate);
        # NOTE: in PatchTSTCrossDelta, self.net.encoder IS the nn.TransformerEncoder
        # (no wrapper layer, unlike Bet 3's PatchTSTEncoder.encoder).
        layer = self.net.encoder.layers[0]
        attn = layer.self_attn
        h = (self.net.proj(xb.to(self.device))
             + self.net.pos[:, self.net.p_idx, :]
             + self.net.ch[:, self.net.c_idx, :])
        h = self.net.drop(h)
        if getattr(layer, "norm_first", True):
            h = layer.norm1(h)
        w = attn.in_proj_weight
        b = attn.in_proj_bias if attn.in_proj_bias is not None else None
        qkv = torch.nn.functional.linear(h, w, b)
        B, Tt, _ = qkv.shape
        q, k, _ = qkv.split(self.D, dim=-1)
        d_k = self.D // attn.num_heads
        q = q.view(B, Tt, attn.num_heads, d_k).transpose(1, 2)
        k = k.view(B, Tt, attn.num_heads, d_k).transpose(1, 2)
        scores = torch.matmul(q, k.transpose(-2, -1)) / (d_k ** 0.5)
        att = torch.softmax(scores, dim=-1)
        ent = float(-(att * (att + 1e-12).log()).sum(dim=-1).mean().item())
        return ent

    def predict(self) -> np.ndarray:
        series = self.history_
        window = series[-CROSS_L:]                 # (336, 7)
        tokens = self._make_tokens(window)
        xb = torch.tensor(tokens[None], dtype=torch.float32, device=self.device)
        with torch.no_grad():
            delta = self.net(xb).cpu().numpy()[0]
        return delta + window[-1, 0]               # OT anchor re-add (D3)
