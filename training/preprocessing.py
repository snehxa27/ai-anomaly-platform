from __future__ import annotations

import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from training.data_loader import load_patient_vitals


class PreprocessingError(Exception):
    pass


VITAL_FEATURES = ["heart_rate", "blood_pressure", "oxygen_level", "temperature"]


def preprocess_and_scale(df, *, output_path: str | Path | None = None) -> np.ndarray:
    missing = [c for c in VITAL_FEATURES if c not in df.columns]
    if missing:
        raise PreprocessingError(f"Missing required feature columns: {missing}")

    X = df[VITAL_FEATURES].copy()
    X = X.apply(pd.to_numeric, errors="coerce")
    X = X.dropna(axis=0, how="any")
    if X.empty:
        raise PreprocessingError("No valid rows after dropping rows with missing feature values.")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X.to_numpy(dtype=np.float64, copy=False))

    base_dir = Path(__file__).resolve().parents[1]
    out = Path(output_path) if output_path is not None else (base_dir / "models" / "scaler.pkl")
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        joblib.dump(scaler, out)
    except Exception as e:
        raise PreprocessingError(f"Failed to save scaler to {out}") from e

    return X_scaled


if __name__ == "__main__":
    try:
        df = load_patient_vitals()
        X_scaled = preprocess_and_scale(df)
        print(f"Scaled shape: {X_scaled.shape}")
        print("Saved scaler to models/scaler.pkl")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise SystemExit(1)
