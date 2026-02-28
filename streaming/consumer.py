from __future__ import annotations

import json
import logging
import os
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import joblib
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from kafka import KafkaConsumer
from kafka.errors import KafkaError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from utils.email_alert import send_alert

EMAIL_TEST_MODE = True
# DEVELOPMENT TEST MODE — cooldown disabled
EMAIL_COOLDOWN_SECONDS = 0
LAST_EMAIL_TIME: float = 0.0

TOPIC_NAME = "patient_vitals"
VITAL_COLUMNS = ["heart_rate", "blood_pressure", "oxygen_level", "temperature"]
DB_NAME = "ai_anomaly_db"
DB_USER = "sneha"


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class InferenceArtifacts:
    scaler: Any
    model: Any


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def create_db_connection() -> Optional[psycopg2.extensions.connection]:
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            host="localhost",
            port=5432,
        )
        conn.autocommit = False
        logger.info("Connected to PostgreSQL database '%s' as user '%s'.", DB_NAME, DB_USER)
        return conn
    except psycopg2.Error as exc:
        logger.error("Failed to connect to PostgreSQL: %s", exc)
        return None


def create_table_if_not_exists(conn: psycopg2.extensions.connection) -> None:
    ddl = """
    CREATE TABLE IF NOT EXISTS anomalies (
        id SERIAL PRIMARY KEY,
        patient_id INTEGER,
        heart_rate FLOAT,
        blood_pressure FLOAT,
        oxygen_level FLOAT,
        temperature FLOAT,
        anomaly_score FLOAT,
        severity VARCHAR(10),
        timestamp TIMESTAMP
    )
    """
    try:
        with conn.cursor() as cur:
            cur.execute(ddl)
        conn.commit()
        logger.info("Ensured anomalies table exists.")
    except psycopg2.Error as exc:
        logger.error("Failed to ensure anomalies table exists: %s", exc)
        try:
            conn.rollback()
        except psycopg2.Error:
            logger.warning("Rollback failed after DDL error.", exc_info=True)


def load_model(  # loads scaler and model once
    *,
    model_path: Path,
    scaler_path: Path,
) -> InferenceArtifacts:
    try:
        scaler = joblib.load(scaler_path)
    except Exception as exc:
        logger.error("Failed to load scaler from %s: %s", scaler_path, exc)
        raise

    try:
        model = joblib.load(model_path)
    except Exception as exc:
        logger.error("Failed to load model from %s: %s", model_path, exc)
        raise

    logger.info("Successfully loaded scaler and model.")
    return InferenceArtifacts(scaler=scaler, model=model)


def create_consumer(bootstrap_servers: Optional[str] = None) -> KafkaConsumer:
    servers = (bootstrap_servers or "localhost:9092").split(",")
    servers = [s.strip() for s in servers if s.strip()]
    if not servers:
        raise ValueError("At least one bootstrap server must be provided.")

    try:
        consumer = KafkaConsumer(
            TOPIC_NAME,
            bootstrap_servers=servers,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="vitals-consumer-group",
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        )
    except KafkaError as exc:
        logger.error("Failed to create Kafka consumer: %s", exc)
        raise

    logger.info("Kafka consumer created for topic '%s' on %s", TOPIC_NAME, servers)
    return consumer


def severity_from_score(score: float) -> str:
    if EMAIL_TEST_MODE:
        if score < 0:
            return "HIGH"
        if score < 0.05:
            return "MEDIUM"
        return "LOW"
    if score < -0.2:
        return "HIGH"
    if score < -0.1:
        return "MEDIUM"
    return "LOW"


def process_message(
    value: dict[str, Any],
    artifacts: InferenceArtifacts,
    conn: Optional[psycopg2.extensions.connection],
) -> None:
    try:
        patient_id = value.get("patient_id")
        if patient_id is None:
            raise ValueError("Missing 'patient_id'")

        # Extract numeric vitals in the required order
        try:
            row = {
                "heart_rate": float(value["heart_rate"]),
                "blood_pressure": float(value["blood_pressure"]),
                "oxygen_level": float(value["oxygen_level"]),
                "temperature": float(value["temperature"]),
            }
        except KeyError as exc:
            raise ValueError(f"Missing vital field: {exc}") from exc
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Non-numeric vital field: {exc}") from exc

        df = pd.DataFrame([row], columns=VITAL_COLUMNS)
        X_scaled = artifacts.scaler.transform(df.values)
        score = float(artifacts.model.decision_function(X_scaled)[0])
        severity = severity_from_score(score)

        print(f"Patient: {patient_id} | Score: {score:.4f} | Severity: {severity}")

        if conn is not None:
            try:
                ts_raw = value.get("timestamp")
                ts_parsed: Optional[datetime]
                if isinstance(ts_raw, str):
                    try:
                        ts_parsed = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
                    except ValueError:
                        ts_parsed = None
                else:
                    ts_parsed = None

                insert_sql = """
                    INSERT INTO anomalies (
                        patient_id,
                        heart_rate,
                        blood_pressure,
                        oxygen_level,
                        temperature,
                        anomaly_score,
                        severity,
                        timestamp
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                with conn.cursor() as cur:
                    cur.execute(
                        insert_sql,
                        (
                            int(patient_id),
                            row["heart_rate"],
                            row["blood_pressure"],
                            row["oxygen_level"],
                            row["temperature"],
                            score,
                            severity,
                            ts_parsed,
                        ),
                    )
                conn.commit()
            except psycopg2.Error as exc:
                logger.warning("Failed to insert anomaly record into DB: %s", exc, exc_info=True)
                try:
                    conn.rollback()
                except psycopg2.Error:
                    logger.warning("Rollback failed after insert error.", exc_info=True)
        else:
            logger.debug("No database connection available; skipping persistence.")

        if severity == "HIGH":
            current_time = time.time()
            global LAST_EMAIL_TIME
            if current_time - LAST_EMAIL_TIME >= EMAIL_COOLDOWN_SECONDS:
                LAST_EMAIL_TIME = current_time
                ts_val = value.get("timestamp")
                ts_str = ts_val.isoformat() if isinstance(ts_val, datetime) else (str(ts_val) if ts_val is not None else "—")
                patient_payload = {
                    "patient_id": patient_id,
                    "heart_rate": row["heart_rate"],
                    "blood_pressure": row["blood_pressure"],
                    "oxygen_level": row["oxygen_level"],
                    "temperature": row["temperature"],
                    "anomaly_score": score,
                    "timestamp": ts_str,
                }
                threading.Thread(target=send_alert, args=(patient_payload,), daemon=True).start()
            else:
                logger.info("Email skipped due to cooldown (patient_id=%s)", patient_id)
    except Exception as exc:
        logger.warning("Failed to process message %s: %s", value, exc, exc_info=True)


def _validate_email_config() -> bool:
    addr = os.getenv("EMAIL_ADDRESS")
    pwd = os.getenv("EMAIL_PASSWORD")
    recv = os.getenv("ALERT_RECEIVER")
    if not addr or not pwd or not recv:
        logger.warning("Email configuration missing — alerts disabled")
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    _validate_email_config()
    base_dir = PROJECT_ROOT
    scaler_path = base_dir / "models" / "scaler.pkl"

    # Support both the current and requested naming for the Isolation Forest model
    preferred_model_path = base_dir / "models" / "isolation_forest_model.pkl"
    fallback_model_path = base_dir / "models" / "isolation_forest.pkl"
    model_path = preferred_model_path if preferred_model_path.exists() else fallback_model_path

    if not scaler_path.exists():
        logger.error("Scaler file not found at %s", scaler_path)
        return 1
    if not model_path.exists():
        logger.error(
            "Model file not found. Tried: %s and %s",
            preferred_model_path,
            fallback_model_path,
        )
        return 1

    db_conn: Optional[psycopg2.extensions.connection] = create_db_connection()
    if db_conn is not None:
        create_table_if_not_exists(db_conn)

    try:
        artifacts = load_model(model_path=model_path, scaler_path=scaler_path)
    except Exception:
        logger.error("Aborting consumer startup due to model/scaler load failure.")
        return 1

    try:
        consumer = create_consumer()
    except Exception:
        logger.error("Aborting consumer startup due to Kafka consumer creation failure.")
        if db_conn is not None:
            try:
                db_conn.close()
            except psycopg2.Error:
                logger.warning("Error while closing DB connection.", exc_info=True)
        return 1

    logger.info("Starting patient vitals consumer loop.")

    try:
        for msg in consumer:
            value = msg.value
            if not isinstance(value, dict):
                logger.warning("Skipping non-dict message: %s", value)
                continue
            process_message(value, artifacts, db_conn)
    except KeyboardInterrupt:
        logger.info("Consumer interrupted by user; shutting down.")
    except Exception as exc:
        logger.exception("Uncaught error in consumer loop: %s", exc)
        return 1
    finally:
        try:
            consumer.close()
        except Exception:
            logger.warning("Error while closing Kafka consumer.", exc_info=True)
        if db_conn is not None:
            try:
                db_conn.close()
            except psycopg2.Error:
                logger.warning("Error while closing DB connection.", exc_info=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())