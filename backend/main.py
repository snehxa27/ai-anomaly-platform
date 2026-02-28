from __future__ import annotations

import argparse
import os
from dataclasses import dataclass

from training.offline.logging_utils import configure_logging
from training.offline.train_offline import train_from_csv_safe


@dataclass(frozen=True)
class Settings:
    environment: str = os.getenv("APP_ENV", "local")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-anomaly-platform")
    parser.add_argument(
        "--env",
        default=os.getenv("APP_ENV", "local"),
        help="Runtime environment (e.g., local/staging/prod).",
    )
    parser.add_argument(
        "--log-level",
        default=os.getenv("LOG_LEVEL", "INFO"),
        help="Logging level (e.g., DEBUG/INFO/WARNING/ERROR).",
    )

    subparsers = parser.add_subparsers(dest="command", required=False)

    train = subparsers.add_parser("train-offline", help="Train an offline anomaly model from CSV.")
    train.add_argument("--data", required=True, help="Path to input CSV.")
    train.add_argument("--output-dir", default="models", help="Directory to write artifacts.")
    train.add_argument("--artifact-name", default="offline_isolation_forest", help="Base name for saved artifacts.")
    train.add_argument("--contamination", type=float, default=0.01, help="Expected anomaly fraction.")
    train.add_argument("--random-state", type=int, default=42, help="Random seed.")
    train.add_argument(
        "--exclude-columns",
        default="",
        help="Comma-separated columns to exclude from features.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    _settings = Settings(environment=args.env)
    configure_logging(args.log_level)

    if args.command == "train-offline":
        exclude = [c.strip() for c in (args.exclude_columns or "").split(",") if c.strip()]
        return train_from_csv_safe(
            csv_path=args.data,
            output_dir=args.output_dir,
            artifact_name=args.artifact_name,
            contamination=args.contamination,
            random_state=args.random_state,
            exclude_columns=exclude,
        )

    print("AI Anomaly Platform Initialized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
