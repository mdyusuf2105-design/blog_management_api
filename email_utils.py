import os
import smtplib
from email.message import EmailMessage


SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "")


def send_email(to_email: str, subject: str, body: str):

    if not all([
        SMTP_HOST,
        SMTP_USERNAME,
        SMTP_PASSWORD,
        EMAIL_FROM
    ]):
        print("Email settings are not configured.")
        return

    message = EmailMessage()

    message["From"] = EMAIL_FROM
    message["To"] = to_email
    message["Subject"] = subject

    message.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(
                SMTP_USERNAME,
                SMTP_PASSWORD
            )
            server.send_message(message)

        print(f"Email sent to {to_email}")

    except Exception as e:
        print(f"Email error: {e}")