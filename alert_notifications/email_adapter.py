import smtplib
from email.message import EmailMessage

class EmailAdapter:
    def __init__(self, server: str, port: int, from_email: str, user: str | None = None, password: str | None = None, to_email: str | None = None):
        self.server, self.port, self.from_email = server, port, from_email
        self.user, self.password, self.to_email = user, password, to_email

    def send(self, subject: str, body: str):
        if not (self.server and self.from_email and self.to_email):
            return
        msg = EmailMessage()
        msg["From"], msg["To"], msg["Subject"] = self.from_email, self.to_email, subject
        msg.set_content(body)
        with smtplib.SMTP(self.server, self.port, timeout=10) as s:
            s.starttls()
            if self.user and self.password:
                s.login(self.user, self.password)
            s.send_message(msg)
