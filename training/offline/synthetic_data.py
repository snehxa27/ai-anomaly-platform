from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SyntheticSpec:
    n_rows: int = 2000
    n_features: int = 8
    anomaly_fraction: float = 0.02
    random_state: int = 42


def make_synthetic_dataframe(spec: SyntheticSpec) -> pd.DataFrame:
    rng = np.random.default_rng(spec.random_state)
    X = rng.normal(loc=0.0, scale=1.0, size=(spec.n_rows, spec.n_features))

    n_anom = max(1, int(spec.n_rows * spec.anomaly_fraction))
    idx = rng.choice(spec.n_rows, size=n_anom, replace=False)
    X[idx] = X[idx] + rng.normal(loc=8.0, scale=2.0, size=(n_anom, spec.n_features))

    cols = [f"f{i}" for i in range(spec.n_features)]
    df = pd.DataFrame(X, columns=cols)
    df["is_synthetic_anomaly"] = 0
    df.loc[idx, "is_synthetic_anomaly"] = 1
    return df

