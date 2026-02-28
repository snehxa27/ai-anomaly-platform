from __future__ import annotations

import sys
from pathlib import Path

import joblib
from sklearn.ensemble import IsolationForest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from training.data_loader import load_patient_vitals
from training.preprocessing import preprocess_and_scale


class TrainingError(Exception):
    pass


def train_isolation_forest(*, contamination: float = 0.05, random_state: int = 42) -> None:
    df = load_patient_vitals()
    X_scaled = preprocess_and_scale(df)

    model = IsolationForest(contamination=contamination, random_state=random_state, n_estimators=300, n_jobs=-1)
    model.fit(X_scaled)

    preds = model.predict(X_scaled)
    n_anomalies = int((preds == -1).sum())

    base_dir = Path(__file__).resolve().parents[1]
    model_path = base_dir / "models" / "isolation_forest.pkl"
    model_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        joblib.dump(model, model_path)
    except Exception as e:
        raise TrainingError(f"Failed to save model to {model_path}") from e

    print(f"Number of anomalies detected: {n_anomalies}")
    print("Training complete. Saved model to models/isolation_forest.pkl")


if __name__ == "__main__":
    try:
        train_isolation_forest()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise SystemExit(1)
