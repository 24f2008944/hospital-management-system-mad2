import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

SMTP_SERVER_HOST = os.getenv("MAIL_SERVER", "localhost")
SMTP_SERVER_PORT = int(os.getenv("MAIL_PORT", 1025))
SENDER_ADDRESS = os.getenv("MAIL_DEFAULT_SENDER", "doctor@donotreply.local")
SMTP_USERNAME = os.getenv("MAIL_USERNAME", "doctor@donotreply.local")
SMTP_PASSWORD = os.getenv("MAIL_PASSWORD", "anypassword")


def send_email_smtp(to_address, subject, message, content="plain", attachment_file=None):
    print(f"DEBUG SMTP HOST: {SMTP_SERVER_HOST}, PORT: {SMTP_SERVER_PORT}, USER: {SMTP_USERNAME}")
    msg = MIMEMultipart()
    msg['From'] = SENDER_ADDRESS
    msg['To'] = to_address
    msg['Subject'] = subject

    if content == "html":
        msg.attach(MIMEText(message, "html"))
    else:
        msg.attach(MIMEText(message, "plain"))

    if attachment_file:
        filename = os.path.basename(attachment_file)
        with open(attachment_file, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={filename}")
        msg.attach(part)

    try:
        with smtplib.SMTP(SMTP_SERVER_HOST, SMTP_SERVER_PORT) as server:
        
            if SMTP_SERVER_HOST != "localhost":
                server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def send_email(to, subject, message, content="plain", attachment_file=None):
    return send_email_smtp(to, subject, message, content, attachment_file)
