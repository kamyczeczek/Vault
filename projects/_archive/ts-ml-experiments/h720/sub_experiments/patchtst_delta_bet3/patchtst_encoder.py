"""Bet 3 — Level-Free PatchTST-style non-linear encoder on orthogonal patches.

Spec (RESEARCH/next-frontier-scout-2026-09-13.md §4, verbatim):
  - Level-free deltas: window[-336:] - anchor, anchor = window[-1] (OT last value).
    Target delta d* = y - anchor; anchor re-added at predict.
  - Patch tokenization: 336 -> 14 tokens (P=24) or 7 tokens (P=48). Each token R^P
    -> linear projection -> R^D + learnable positional encoding.
  - Encoder: 2-layer Transformer (primary P24D32), heads=2, D=32, FFN=64,
    dropout=0.30, stochastic_depth=0.10, weight_decay=1e-2 on non-norm weights,
    attention dropout 0.2, NO causal mask. Ablation: 1-layer P48D16.
  - Decoder: pooled token mean -> per-horizon linear head -> R^720 delta, + anchor.
  - Capacity ~28k params primary (under-parameterized by design).
  - Train: AdamW lr=3e-4, early stopping on val delta-MAE, grad clip 1.0, batch 64.
    Deterministic (torch.manual_seed(0), numpy 0).

Reuses patch_embed.embed_window for the level-free shift + standardization so the
representation is consistent with the Bet 2 pipeline (train-only mu/sigma).

The encoder consumes a pre-computed patch-token tensor X of shape
(N, n_tokens, P) where each token is the raw (or pre-shifted) patch, then projects
to D, adds positional encoding, runs the Transformer, pools, and regresses the
delta horizon. All S-26 level-free discipline is preserved outside this module.
"""
from __future__ import annotations

import copy
import numpy as np
import torch
import torch.nn as nn


def _set_deterministic():
    torch.manual_seed(0)
    np.random.seed(0)
    torch.use_deterministic_algorithms(True, warn_only=True)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


class _StochasticDepth(nn.Module):
    """Drop-path with survival prob p (mirrors torchvision; keeps mypy clean)."""

    def __init__(self, p: float = 0.1):
        super().__init__()
        self.p = float(p)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if not self.training or self.p == 0.0:
            return x
        keep = 1.0 - self.p
        shape = (x.shape[0],) + (1,) * (x.ndim - 1)
        mask = torch.empty(shape, dtype=x.dtype, device=x.device).bernoulli_(keep)
        return x * (mask / keep)


class PatchTSTEncoder(nn.Module):
    """Shallow bidirectional Transformer over patch tokens -> pooled representation.

    input  : X (N, T, P) raw patch tokens (T = n_tokens, P = patch size)
    output : pooled (N, D) mean over token positions
    """

    def __init__(self, P: int, D: int, n_layers: int, n_heads: int,
                 ffn: int, dropout: float, attn_dropout: float,
                 stochastic_depth: float):
        super().__init__()
        assert D % n_heads == 0, "D must be divisible by n_heads"
        self.P = P
        self.D = D
        self.n_layers = n_layers
        self.n_tokens = None  # set on first forward for pos encoding

        self.proj = nn.Linear(P, D)  # token projection (non-norm, weight-decayed)
        self.pos = nn.Parameter(torch.zeros(1, 500, D))  # learnable pos encoding
        self.drop = nn.Dropout(dropout)

        layer = nn.TransformerEncoderLayer(
            d_model=D, nhead=n_heads, dim_feedforward=ffn,
            dropout=dropout, activation="gelu", batch_first=True,
            norm_first=True,
        )
        # attention dropout lives on the self-attention submodule
        layer.self_attn.dropout = attn_dropout
        self.encoder = nn.TransformerEncoder(layer, num_layers=n_layers)

        self.stoch = nn.ModuleList([_StochasticDepth(stochastic_depth)
                                    for _ in range(n_layers)])

    def forward(self, X: torch.Tensor) -> torch.Tensor:
        # X: (N, T, P)
        T = X.shape[1]
        h = self.proj(X) + self.pos[:, :T, :]   # (N, T, D)
        h = self.drop(h)
        h = self.encoder(h)                      # (N, T, D)
        # stochastic depth on the pooled residual signal (no-op at inference)
        for sd in self.stoch:
            h = sd(h)
        pooled = h.mean(dim=1)                   # (N, D)
        return pooled


class PatchTSTDelta(nn.Module):
    """Full per-horizon delta forecaster built on PatchTSTEncoder."""

    def __init__(self, P: int = 24, D: int = 32, n_layers: int = 2,
                 n_heads: int = 2, ffn: int = 64, H: int = 720,
                 dropout: float = 0.30, attn_dropout: float = 0.2,
                 stochastic_depth: float = 0.10):
        super().__init__()
        self.P = P
        self.D = D
        self.H = H
        self.encoder = PatchTSTEncoder(
            P=P, D=D, n_layers=n_layers, n_heads=n_heads, ffn=ffn,
            dropout=dropout, attn_dropout=attn_dropout,
            stochastic_depth=stochastic_depth,
        )
        self.head = nn.Linear(D, H)  # per-horizon linear head (non-norm)
        # weight decay grouping: norm-free params (proj, head, pos) decay; none on norms
        self._build_param_groups()

    def _build_param_groups(self):
        decay, no_decay = [], []
        for name, p in self.named_parameters():
            if not p.requires_grad:
                continue
            if "norm" in name or name == "encoder.pos":
                no_decay.append(p)
            else:
                decay.append(p)
        self.param_groups = [
            {"params": decay, "weight_decay": 1e-2},
            {"params": no_decay, "weight_decay": 0.0},
        ]

    def forward(self, X: torch.Tensor) -> torch.Tensor:
        # X: (N, T, P) -> delta pred (N, H)
        return self.head(self.encoder(X))

    def count_params(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


class PatchTSTModel:
    """Fit/predict wrapper using the S-26 level-free delta convention (S-21b pattern).

    The member is trained ONCE on a windowed training series (8545 or 11425) and
    evaluated on rolling origins by swapping the trailing history (S-20-clean).
    Inputs are level-free deltas computed inside fit/predict; the encoder only ever
    sees patch tokens of the shifted window.
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
        self.target_index = 0
        self.horizon_ = H
        self.attention_entropies_ = []
        self.train_val_gap_ = None

    # ----- internal tokenization (level-free, standardized) -----
    def _make_tokens(self, window_1d: np.ndarray) -> np.ndarray:
        """window_1d: (L,) OT, anchor = window[-1]; shift, patch, standardize."""
        anchor = window_1d[-1]
        shifted = window_1d - anchor  # (L,)
        # patch-mean-pool manually to avoid channel machinery (single channel)
        L = shifted.shape[0]
        n_tokens = L // self.patch_size
        tokens = shifted[: n_tokens * self.patch_size].reshape(n_tokens, self.patch_size)
        tokens = (tokens - self.mu) / self.sigma  # standardize with train-only stats
        return tokens.astype(np.float32)

    def _build_dataset(self, series: np.ndarray) -> tuple[torch.Tensor, torch.Tensor, np.ndarray]:
        L = self.patch_size * (336 // self.patch_size)  # 336
        assert 336 % self.patch_size == 0
        Xs, Ys, anc = [], [], []
        for end in range(L, len(series) - self.H + 1):
            window = series[end - L:end]
            anchor = window[-1]
            tokens = self._make_tokens(window)
            target = series[end:end + self.H] - anchor
            Xs.append(tokens)
            Ys.append(target.astype(np.float32))
            anc.append(anchor)
        X = torch.tensor(np.stack(Xs), dtype=torch.float32)
        Y = torch.tensor(np.stack(Ys), dtype=torch.float32)
        return X, Y, np.asarray(anc)

    def fit(self, y, *, horizon: int, target_index: int = 0) -> "PatchTSTModel":
        series = np.asarray(y, dtype=float)
        if series.ndim == 2:
            series = series[:, target_index]
        _set_deterministic()
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

    def _attention_entropy(self, xb: torch.Tensor) -> float:
        # attention entropy (nats) of the first encoder layer, averaged over heads/tokens
        layer = self.net.encoder.encoder.layers[0]
        attn = layer.self_attn
        T = xb.shape[1]
        h = self.net.encoder.proj(xb.to(self.device)) + self.net.encoder.pos[:, :T, :]
        h = self.net.encoder.drop(h)
        if getattr(layer, "norm_first", True):
            h = layer.norm1(h)
        # nn.MultiheadAttention packs Q,K,V into one in_proj linear
        w = attn.in_proj_weight  # (3*E, E)
        b = attn.in_proj_bias if attn.in_proj_bias is not None else None
        qkv = torch.nn.functional.linear(h, w, b)  # (B, T, 3E)
        B, Tt, _ = qkv.shape
        q, k, _ = qkv.split(self.D, dim=-1)
        d_k = self.D // attn.num_heads
        q = q.view(B, Tt, attn.num_heads, d_k).transpose(1, 2)
        k = k.view(B, Tt, attn.num_heads, d_k).transpose(1, 2)
        scores = torch.matmul(q, k.transpose(-2, -1)) / (d_k ** 0.5)
        att = torch.softmax(scores, dim=-1)  # (B, H, T, T)
        ent = float(-(att * (att + 1e-12).log()).sum(dim=-1).mean().item())
        return ent

    def predict(self) -> np.ndarray:
        series = self.history_
        L = 336
        window = series[-L:]
        tokens = self._make_tokens(window)
        xb = torch.tensor(tokens[None], dtype=torch.float32, device=self.device)
        with torch.no_grad():
            delta = self.net(xb).cpu().numpy()[0]
        return delta + window[-1]


def ffn_for(patch_size: int, D: int) -> int:
    """FFN width scales with capacity: primary P24/D32 -> 64, ablation P48/D16 -> 32."""
    if patch_size == 24 and D == 32:
        return 64
    if patch_size == 48 and D == 16:
        return 32
    return 4 * D
