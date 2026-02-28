from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from training.offline.errors import DataValidationError


@dataclass(frozen=True)
class FeatureSpec:
    numeric_columns: list[str]


def infer_numeric_features(df: pd.DataFrame, exclude: set[str] | None = None) -> FeatureSpec:
    exclude = exclude or set()
    candidates = df.select_dtypes(include=["number"]).columns.tolist()
    numeric_columns = [c for c in candidates if c not in exclude]
    if not numeric_columns:
        raise DataValidationError("No numeric feature columns found in dataset.")
    return FeatureSpec(numeric_columns=numeric_columns)


def select_features(df: pd.DataFrame, spec: FeatureSpec) -> pd.DataFrame:
    missing = [c for c in spec.numeric_columns if c not in df.columns]
    if missing:
        raise DataValidationError(f"Missing expected feature columns: {missing}")
    return df[spec.numeric_columns].copy()

