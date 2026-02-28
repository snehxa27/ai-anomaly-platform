from __future__ import annotations

import hashlib
import logging
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from training.offline.artifacts import save_artifacts
from training.offline.errors import DataValidationError, TrainingError
from training.offline.features import FeatureSpec, infer_numeric_features, select_features
from training.offline.io import load_csv
from training.offline.model import build_isolation_forest_pipeline

logger = logging.getLogger(__name__)


def _fingerprint_dataframe(df: pd.DataFrame, *, max_rows: int = 5000) -> str:
    sample = df.head(max_rows)
    payload = pd.util.hash_pandas_object(sample, index=True).values.tobytes()
    return hashlib.sha256(payload).hexdigest()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def train_from_csv(
    *,
    csv_path: str | Path,
    output_dir: str | Path = "models",
    artifact_name: str = "offline_isolation_forest",
    contamination: float = 0.01,
    random_state: int = 42,
    exclude_columns: list[str] | None = None,
) -> dict[str, str]:
    df = load_csv(csv_path)
    exclude = set(exclude_columns or [])
    spec: FeatureSpec = infer_numeric_features(df, exclude=exclude)
    X_df = select_features(df, spec)
    if X_df.shape[0] < 10:
        raise DataValidationError("Not enough rows to train a stable model (need at least 10).")

    X = X_df.to_numpy(dtype=np.float64, copy=False)
    pipeline = build_isolation_forest_pipeline(
        contamination=contamination,
        random_state=random_state,
    )
    pipeline.fit(X)

    metadata = {
        "artifact_name": artifact_name,
        "created_at_utc": _utc_now_iso(),
        "trainer": "training.offline.train_offline:train_from_csv",
        "model_type": "IsolationForest",
        "contamination": contamination,
        "random_state": random_state,
        "n_rows": int(X_df.shape[0]),
        "n_features": int(X_df.shape[1]),
        "features": asdict(spec),
        "data_fingerprint_sha256": _fingerprint_dataframe(df),
    }
    paths = save_artifacts(
        output_dir=output_dir,
        artifact_name=artifact_name,
        pipeline=pipeline,
        metadata=metadata,
    )
    logger.info("Saved model artifact: %s", paths.model_path)
    logger.info("Saved metadata: %s", paths.metadata_path)
    return {"model_path": str(paths.model_path), "metadata_path": str(paths.metadata_path)}


def train_from_csv_safe(**kwargs) -> int:
    try:
        train_from_csv(**kwargs)
        return 0
    except TrainingError as e:
        logger.error(str(e))
        return 2
    except Exception:
        logger.exception("Unexpected failure during training.")
        return 1

