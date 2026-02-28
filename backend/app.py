
from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from typing import Generator, Any, Dict

import psycopg2
from flask import Flask, jsonify
from psycopg2.extras import RealDictCursor


app = Flask(__name__)
logger = logging.getLogger(__name__)

print("🔥 APP FILE EXECUTING 🔥")

DB_NAME = os.getenv("DB_NAME", "ai_anomaly_db")
DB_USER = os.getenv("DB_USER", "sneha")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")


def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD or None,
        host=DB_HOST,
        port=DB_PORT,
    )


@contextmanager
def db_cursor() -> Generator:
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            yield cur
    finally:
        conn.close()


def convert_row(row: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(row)
    if "timestamp" in result and result["timestamp"]:
        result["timestamp"] = result["timestamp"].isoformat()
    if "anomaly_score" in result and result["anomaly_score"] is not None:
        result["anomaly_score"] = float(result["anomaly_score"])
    if "temperature" in result and result["temperature"] is not None:
        result["temperature"] = float(result["temperature"])
    return result


# ------------------ EXISTING ------------------

@app.route("/api/anomalies", methods=["GET"])
def get_anomalies():
    with db_cursor() as cur:
        cur.execute("""
            SELECT id, patient_id, heart_rate, blood_pressure,
                   oxygen_level, temperature,
                   anomaly_score, severity, timestamp
            FROM anomalies
            ORDER BY timestamp DESC NULLS LAST
            LIMIT 100
        """)
        rows = cur.fetchall()
    return jsonify([convert_row(r) for r in rows])


@app.route("/api/patient/<int:patient_id>", methods=["GET"])
def get_patient(patient_id):
    with db_cursor() as cur:
        cur.execute("""
            SELECT id, patient_id, heart_rate, blood_pressure,
                   oxygen_level, temperature,
                   anomaly_score, severity, timestamp
            FROM anomalies
            WHERE patient_id = %s
            ORDER BY timestamp DESC NULLS LAST
        """, (patient_id,))
        rows = cur.fetchall()
    return jsonify([convert_row(r) for r in rows])


# ------------------ NEW DASHBOARD ROUTES ------------------

@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    with db_cursor() as cur:
        cur.execute("""
            SELECT
                COUNT(DISTINCT patient_id) AS active_patients,
                COUNT(*) FILTER (WHERE severity='HIGH') AS high_alerts,
                COALESCE(AVG(anomaly_score),0) AS avg_anomaly_score,
                MAX(timestamp) FILTER (WHERE severity='HIGH') AS last_alert_time
            FROM anomalies
        """)
        row = cur.fetchone()

    result = dict(row)
    if result["last_alert_time"]:
        result["last_alert_time"] = result["last_alert_time"].isoformat()
    result["avg_anomaly_score"] = float(result["avg_anomaly_score"])
    return jsonify(result)


@app.route("/api/severity-distribution", methods=["GET"])
def severity_distribution():
    with db_cursor() as cur:
        cur.execute("""
            SELECT severity, COUNT(*) AS count
            FROM anomalies
            GROUP BY severity
        """)
        rows = cur.fetchall()

    distribution = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for r in rows:
        distribution[r["severity"]] = r["count"]
    return jsonify(distribution)


@app.route("/api/trend/anomaly", methods=["GET"])
def anomaly_trend():
    with db_cursor() as cur:
        cur.execute("""
            SELECT timestamp, anomaly_score
            FROM anomalies
            ORDER BY timestamp DESC
            LIMIT 50
        """)
        rows = cur.fetchall()

    rows.reverse()

    return jsonify([
        {
            "timestamp": r["timestamp"].isoformat() if r["timestamp"] else None,
            "anomaly_score": float(r["anomaly_score"])
        }
        for r in rows
    ])


@app.route("/api/trend/vitals", methods=["GET"])
def vitals_trend():
    with db_cursor() as cur:
        cur.execute("""
            SELECT timestamp, heart_rate, oxygen_level,
                   temperature, blood_pressure
            FROM anomalies
            ORDER BY timestamp DESC
            LIMIT 50
        """)
        rows = cur.fetchall()

    rows.reverse()

    return jsonify([
        {
            "timestamp": r["timestamp"].isoformat() if r["timestamp"] else None,
            "heart_rate": r["heart_rate"],
            "oxygen_level": r["oxygen_level"],
            "temperature": float(r["temperature"]) if r["temperature"] else None,
            "blood_pressure": r["blood_pressure"]
        }
        for r in rows
    ])


@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="0.0.0.0", port=8000)