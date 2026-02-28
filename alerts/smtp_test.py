"""Test Gmail SMTP login capability. Does not send email."""

from pathlib import Path

from dotenv import load_dotenv
import os
import smtplib

load_dotenv(Path(__file__).resolve().parent / ".env")

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def main() -> None:
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")

    if not email_address or not email_password:
        print("ERROR: EMAIL_ADDRESS and EMAIL_PASSWORD must be set in .env")
        return

    print("Connecting to Gmail SMTP...")
    server = None
    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
        server.ehlo()
        server.starttls()
        print("TLS started")
        server.ehlo()
        server.login(email_address, email_password)
        print("Login successful")
        print("SMTP test completed successfully")
    except smtplib.SMTPAuthenticationError as e:
        print(f"ERROR: SMTP authentication failed — check App Password.\n  {e}")
    except smtplib.SMTPServerDisconnected as e:
        print(f"ERROR: SMTP server disconnected — possible Gmail security block.\n  {e}")
    except smtplib.SMTPException as e:
        print(f"ERROR: General SMTP error: {e}")
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
    finally:
        if server:
            try:
                server.quit()
                print("Connection closed safely.")
            except Exception:
                print("Connection closed (quit raised).")


if __name__ == "__main__":
    main()
