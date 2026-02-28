from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


class DataLoaderError(Exception):
    pass


def load_patient_vitals(csv_path: str | Path | None = None) -> pd.DataFrame:
    base_dir = Path(__file__).resolve().parents[1]
    path = Path(csv_path) if csv_path is not None else (base_dir / "data" / "patient_vitals.csv")

    if not path.exists():
        raise DataLoaderError(f"CSV file not found: {path}")
    if path.is_dir():
        raise DataLoaderError(f"Expected a CSV file but got a directory: {path}")

    try:
        df = pd.read_csv(path)
    except Exception as e:
        raise DataLoaderError(f"Failed to read CSV: {path}") from e

    if df.empty:
        raise DataLoaderError("Dataset is empty.")

    missing_summary = df.isna().sum()
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print("Missing values per column:")
    print(missing_summary.to_string())

    df = df.dropna(how="all").reset_index(drop=True)
    if df.empty:
        raise DataLoaderError("Dataset became empty after dropping fully-empty rows.")

    return df


if __name__ == "__main__":
    try:
        load_patient_vitals()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise SystemExit(1)
