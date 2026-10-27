"""Methods package: unified forecaster registry and factory.

All forecasters implement ``BaseForecaster``:

    model = SomeForecaster(**hyperparams)
    model.fit(y, horizon=H).predict()   -> np.ndarray (H,)
"""

from .base import BaseForecaster
from .baselines import Persistence, seasonal_forecast, seasonal_score
from .ensemble import CrossFamilyEnsemble
from .fits import FITSForecaster
from .knn_models import (
    LAGS,
    BalancedLagEnsembleKNN,
    HeuristicLagDecisionTree,
    HeuristicLagKNN,
    HeuristicLagKNNRecursive,
    HeuristicLagRandomForest,
    TemporalLagKNN,
)
from .multirate import MultiRateELM
from .multirate_rbf import MultiRateRBF
from .neural_models import DLinear, HeuristicLagELM, HeuristicLagELMTree, NLinear, RLinear
from .nlinear_knn import NLinearKNNHybrid
from .nlinear_rf import NLinearRF
from .rbf import RBFELM
from .residual import SeasonalResidualELM

REGISTRY: dict[str, type[BaseForecaster]] = {
    "persistence": Persistence,
    "heuristic_lag_knn": HeuristicLagKNN,
    "heuristic_lag_knn_recursive": HeuristicLagKNNRecursive,
    "heuristic_lag_rf": HeuristicLagRandomForest,
    "heuristic_lag_tree": HeuristicLagDecisionTree,
    "temporal_lag_knn": TemporalLagKNN,
    "dlinear": DLinear,
    "nlinear": NLinear,
    "rlinear": RLinear,
    "fits": FITSForecaster,
    "cross_family_ensemble": CrossFamilyEnsemble,
    "multirate_elm": MultiRateELM,
    "rbf_elm": RBFELM,
    "seasonal_residual_elm": SeasonalResidualELM,
    "heuristic_lag_elm": HeuristicLagELM,
    "heuristic_lag_elm_tree": HeuristicLagELMTree,
    "multirate_rbf": MultiRateRBF,
    "nlinear_rf": NLinearRF,
    "nlinear_knn": NLinearKNNHybrid,
}


def make_forecaster(name: str, horizon: int | None = None, **kwargs) -> BaseForecaster:
    """Factory: return a forecaster instance.

    ``horizon`` is accepted for backwards compatibility with old runners
    but ignored — it belongs to :meth:`BaseForecaster.fit`.
    """
    cls = REGISTRY.get(name)
    if cls is None:
        raise ValueError(
            f"unknown forecaster {name!r}; available: {sorted(REGISTRY)}"
        )
    if horizon is not None:
        kwargs.pop("horizon", None)
    return cls(**kwargs)


__all__ = [
    "BaseForecaster",
    "Persistence",
    "HeuristicLagKNN",
    "HeuristicLagKNNRecursive",
    "TemporalLagKNN",
    "HeuristicLagRandomForest",
    "HeuristicLagDecisionTree",
    "BalancedLagEnsembleKNN",
    "DLinear",
    "NLinear",
    "RLinear",
    "FITSForecaster",
    "CrossFamilyEnsemble",
    "HeuristicLagELM",
    "LAGS",
    "REGISTRY",
    "make_forecaster",
    "seasonal_forecast",
    "seasonal_score",
]
