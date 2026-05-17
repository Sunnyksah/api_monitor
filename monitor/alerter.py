import os
import smtplib
import requests as req
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from monitor.logger import get_logger

log = get_logger("alerter")

def send_email(subject: str, body: str):
    if os.getenv("EMAIL_ENABLED", "false").lower() != "true":
        return
    try:
        sender = os.environ("EMAIL_SENDER")
        password = os.environ("EMAIL_PASSWORD")
        recipient = os.environ("EMAIL_RECIPIENT")
        host = os.getenv("SMTP_HOST", "smtp@gmail.com")
        port = int(os.getenv("SMTP_PORT", 587))

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Monitor Alert: {subject}"
        msg["From"] = sender
        msg["To"] = recipient
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())

        log.info(f"Email alert sent -> {recipient}: {subject}")
    except Exception as e:
        log.error(f"Email send failed: {e}")


def send_telegram(message: str):
    if os.getenv("TELEGRAM_ENABLED", "false").lower() != "true":
        return
    try:
        token = os.environ["TELEGRAM_BOT_TOKEN"]
        chat_id = os.environ["TELEGRAM_CHAT_ID"]
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
        resp = req.post(url, json=payload, timeout=10)
        resp.raise_for_status()

        log.info(f"Telegram alert sent to chat {chat_id}")
    except Exception as e:
        log.error(f"Telegram send failed: {e}")


def dispatch_alert(alert: dict, monitor_name: str):
    subject = f"{monitor_name} - {alert['type'].upper()}"
    body = alert["message"]

    send_email(subject, body)
    send_telegram(f"<b>{subject}</b>\n\n{body}")