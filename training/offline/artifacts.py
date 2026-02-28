from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import joblib

from training.offline.errors import ArtifactSaveError


@dataclass(frozen=True)
class ArtifactPaths:
    model_path: Path
    metadata_path: Path


def ensure_dir(path: Path) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise ArtifactSaveError(f"Failed to create directory: {path}") from e


def save_artifacts(
    *,
    output_dir: str | Path,
    artifact_name: str,
    pipeline: Any,
    metadata: dict[str, Any],
) -> ArtifactPaths:
    out = Path(output_dir)
    ensure_dir(out)
    model_path = out / f"{artifact_name}.joblib"
    metadata_path = out / f"{artifact_name}.metadata.json"
    try:
        joblib.dump(pipeline, model_path)
    except Exception as e:
        raise ArtifactSaveError(f"Failed to save joblib artifact: {model_path}") from e
    try:
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except Exception as e:
        raise ArtifactSaveError(f"Failed to save metadata: {metadata_path}") from e
    return ArtifactPaths(model_path=model_path, metadata_path=metadata_path)

