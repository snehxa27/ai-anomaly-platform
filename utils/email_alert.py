from __future__ import annotations

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def send_alert(patient_data: dict) -> None:
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")
    alert_receiver = os.getenv("ALERT_RECEIVER")

    if not email_address or not email_password or not alert_receiver:
        logger.warning("Email alert skipped: EMAIL_ADDRESS, EMAIL_PASSWORD, or ALERT_RECEIVER not set in .env")
        return

    patient_id = patient_data.get("patient_id", "—")
    logger.info("Sending HIGH severity alert email for patient_id=%s", patient_id)
    heart_rate = patient_data.get("heart_rate", "—")
    blood_pressure = patient_data.get("blood_pressure", "—")
    oxygen_level = patient_data.get("oxygen_level", "—")
    temperature = patient_data.get("temperature", "—")
    anomaly_score = patient_data.get("anomaly_score", "—")
    timestamp = patient_data.get("timestamp", "—")

    body = f"""
HIGH SEVERITY ANOMALY ALERT

Patient ID:      {patient_id}
Heart Rate:      {heart_rate}
Blood Pressure:  {blood_pressure}
Oxygen Level:    {oxygen_level}
Temperature:     {temperature}
Anomaly Score:   {anomaly_score}
Timestamp:       {timestamp}

—
AI Healthcare Monitoring System
""".strip()

    msg = MIMEMultipart()
    msg["From"] = email_address
    msg["To"] = alert_receiver
    msg["Subject"] = f"ALERT: High Severity Anomaly — Patient {patient_id}"
    msg.attach(MIMEText(body, "plain"))

    server = None
    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(email_address, email_password)
        server.sendmail(email_address, alert_receiver, msg.as_string())
        logger.info("SMTP sendmail executed for patient_id=%s", patient_id)
        server.quit()
        logger.info("SMTP connection closed for patient_id=%s", patient_id)
        logger.info("Email alert sent successfully for patient_id=%s", patient_id)
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed — check App Password.")
    except smtplib.SMTPServerDisconnected:
        logger.error("SMTP server disconnected — possible Gmail security block.")
    except smtplib.SMTPException as e:
        logger.error("General SMTP error: %s", e)
    except Exception as exc:
        logger.warning("Unexpected error sending alert for patient_id=%s: %s", patient_id, exc)
    finally:
        if server:
            try:
                server.quit()
            except Exception:
                pass
    logger.info("send_alert() finished for patient_id=%s", patient_id)
