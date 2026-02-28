from __future__ import annotations

from pathlib import Path

import pandas as pd

from training.offline.errors import DataLoadError


def load_csv(path: str | Path) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise DataLoadError(f"CSV not found: {p}")
    if p.is_dir():
        raise DataLoadError(f"Expected a file, got directory: {p}")
    try:
        df = pd.read_csv(p)
    except Exception as e:
        raise DataLoadError(f"Failed to read CSV: {p}") from e
    if df.empty:
        raise DataLoadError(f"CSV is empty: {p}")
    return df

