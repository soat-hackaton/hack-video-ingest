from email.message import EmailMessage
import os
import smtplib
from typing import List, Optional
from src.core.interfaces.email_sender import EmailSender


class GmailSmtpEmailSender(EmailSender):

    def __init__(self):
        self.email = os.getenv("GMAIL_EMAIL_ADDRESS")
        self.app_password = os.getenv("GMAIL_APP_PASSWORD").replace(" ", "").replace("\xa0", "").strip()
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 587

    def send(
        self,
        to_emails: List[str],
        subject: str,
        text: str,
        html: Optional[str] = None
    ) -> None:

        msg = EmailMessage()
        msg["From"] = self.email
        msg["To"] = ", ".join(to_emails)
        msg["Subject"] = subject

        msg.set_content(text, charset="utf-8")

        if html:
            msg.add_alternative(html, subtype="html", charset="utf-8")

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.email, self.app_password)
            server.send_message(msg)