import os
import smtplib
from email.message import EmailMessage

from app.application.errors import RepositoryError


class SmtpEmailSender:
    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
        from_email: str | None = None,
        use_tls: bool | None = None,
    ) -> None:
        self._host = host or os.getenv("SMTP_HOST")
        self._port = port or int(os.getenv("SMTP_PORT", "587"))
        self._username = username or os.getenv("SMTP_USERNAME")
        self._password = password or os.getenv("SMTP_PASSWORD")
        self._from_email = from_email or os.getenv("SMTP_FROM_EMAIL", "andyricardog234@gmail.com")
        self._use_tls = use_tls if use_tls is not None else os.getenv("SMTP_USE_TLS", "true").lower() == "true"

    def send_email(self, to: str, subject: str, html: str) -> None:
        if not self._host or not self._username or not self._password:
            raise RepositoryError("SMTP no esta configurado. Define SMTP_HOST, SMTP_USERNAME y SMTP_PASSWORD.")

        message = EmailMessage()
        message["From"] = self._from_email
        message["To"] = to
        message["Subject"] = subject
        message.set_content("Tu cliente de correo no soporta HTML.")
        message.add_alternative(html, subtype="html")

        try:
            with smtplib.SMTP(self._host, self._port, timeout=20) as server:
                if self._use_tls:
                    server.starttls()
                server.login(self._username, self._password)
                server.send_message(message)
        except OSError as exc:
            raise RepositoryError("No se pudo enviar el correo de bienvenida.") from exc
