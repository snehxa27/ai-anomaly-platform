from __future__ import annotations

import argparse
import json
import logging
import random
import signal
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Iterable

from kafka import KafkaProducer
from kafka.errors import KafkaError


logger = logging.getLogger(__name__)

TOPIC_NAME = "patient_vitals"


@dataclass(frozen=True)
class PatientVitals:
    patient_id: int
    heart_rate: int
    blood_pressure: int
    oxygen_level: int
    temperature: float
    timestamp: str


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def generate_patient_vitals(num_patients: int) -> Iterable[list[PatientVitals]]:
    while True:
        batch: list[PatientVitals] = []
        ts = utc_now_iso()
        for pid in range(1, num_patients + 1):
            batch.append(
                PatientVitals(
                    patient_id=pid,
                    heart_rate=random.randint(55, 140),
                    blood_pressure=random.randint(90, 180),
                    oxygen_level=random.randint(88, 100),
                    temperature=round(random.uniform(36.0, 40.0), 1),
                    timestamp=ts,
                )
            )
        yield batch


def create_producer(bootstrap_servers: str) -> KafkaProducer:
    servers = [s.strip() for s in bootstrap_servers.split(",") if s.strip()]
    if not servers:
        raise ValueError("At least one bootstrap server must be provided.")
    try:
        producer = KafkaProducer(
            bootstrap_servers=servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda v: str(v).encode("utf-8") if v is not None else None,
            linger_ms=10,
            retries=3,
            acks="all",
        )
    except KafkaError as e:
        logger.exception("Failed to create Kafka producer.")
        raise
    logger.info("Kafka producer created for servers: %s", servers)
    return producer


def _log_send_error(exc: BaseException, patient_id: int) -> None:
    logger.error("Failed to send message for patient_id=%s: %s", patient_id, exc)


def run(
    *,
    bootstrap_servers: str,
    interval_seconds: float = 2.0,
    num_patients: int = 100,
) -> None:
    stop = {"flag": False}

    def handle_signal(signum: int, _frame: object) -> None:
        logger.info("Received signal %s, shutting down producer loop.", signum)
        stop["flag"] = True

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    producer = create_producer(bootstrap_servers)
    batches = generate_patient_vitals(num_patients)

    logger.info(
        "Starting patient vitals producer: topic=%s patients=%s interval=%.2fs",
        TOPIC_NAME,
        num_patients,
        interval_seconds,
    )

    try:
        for batch in batches:
            if stop["flag"]:
                break
            start = time.time()
            for vitals in batch:
                payload = asdict(vitals)
                future = producer.send(
                    TOPIC_NAME,
                    key=vitals.patient_id,
                    value=payload,
                )
                future.add_errback(_log_send_error, patient_id=vitals.patient_id)
            try:
                producer.flush(timeout=10.0)
            except KafkaError as e:
                logger.error("Error during flush: %s", e)
            elapsed = time.time() - start
            sleep_for = max(0.0, interval_seconds - elapsed)
            if sleep_for:
                time.sleep(sleep_for)
    finally:
        logger.info("Closing Kafka producer.")
        try:
            producer.flush(timeout=5.0)
        except KafkaError:
            logger.warning("Flush failed during shutdown.", exc_info=True)
        producer.close()
        logger.info("Producer closed.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="patient-vitals-producer")
    parser.add_argument(
        "--bootstrap-servers",
        default="localhost:9092",
        help="Comma-separated list of Kafka bootstrap servers.",
    )
    parser.add_argument(
        "--interval-seconds",
        type=float,
        default=2.0,
        help="Interval between batches of vitals (seconds).",
    )
    parser.add_argument(
        "--num-patients",
        type=int,
        default=100,
        help="Number of simulated patients.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (DEBUG, INFO, WARNING, ERROR).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.log_level)
    try:
        run(
            bootstrap_servers=args.bootstrap_servers,
            interval_seconds=args.interval_seconds,
            num_patients=args.num_patients,
        )
        return 0
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
        return 0
    except Exception as e:
        logger.exception("Uncaught error in producer: %s", e)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

