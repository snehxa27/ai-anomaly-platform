from __future__ import annotations

import sys
from pathlib import Path

import joblib
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


VITAL_FEATURES = ["heart_rate", "blood_pressure", "oxygen_level", "temperature"]


class InferenceError(Exception):
    pass


def severity_from_score(score: float) -> str:
    if score < -0.2:
        return "High"
    if score < -0.1:
        return "Medium"
    return "Low"


def run_inference(sample: dict) -> None:
    base_dir = Path(__file__).resolve().parents[1]
    scaler_path = base_dir / "models" / "scaler.pkl"
    model_path = base_dir / "models" / "isolation_forest.pkl"

    if not scaler_path.exists():
        raise InferenceError(f"Missing scaler artifact: {scaler_path}")
    if not model_path.exists():
        raise InferenceError(f"Missing model artifact: {model_path}")

    scaler = joblib.load(scaler_path)
    model = joblib.load(model_path)

    missing = [k for k in VITAL_FEATURES if k not in sample]
    if missing:
        raise InferenceError(f"Missing keys in sample input: {missing}")

    x = np.array([[float(sample[k]) for k in VITAL_FEATURES]], dtype=np.float64)
    x_scaled = scaler.transform(x)

    score = float(model.decision_function(x_scaled)[0])
    pred = int(model.predict(x_scaled)[0])
    label = "Anomaly" if pred == -1 else "Normal"

    print(f"Raw score: {score:.6f}")
    print(f"Anomaly label: {label}")
    print(f"Severity level: {severity_from_score(score)}")


if __name__ == "__main__":
    try:
        sample_patient_vitals = {
            "heart_rate": 125,
            "blood_pressure": 170,
            "oxygen_level": 90,
            "temperature": 39.2,
        }
        run_inference(sample_patient_vitals)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise SystemExit(1)
