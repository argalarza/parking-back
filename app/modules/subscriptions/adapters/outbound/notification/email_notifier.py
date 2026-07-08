from html import escape

from app.modules.notifications.application.ports import EmailSender


class SubscriberEmailNotifier:
    def __init__(self, email_sender: EmailSender) -> None:
        self._email_sender = email_sender

    def send_initial_credentials(self, full_name: str, email: str, password: str) -> None:
        self._email_sender.send_email(
            to=email,
            subject="Bienvenido a BIOPARK",
            html=self._build_welcome_email(
                full_name=full_name,
                email=email,
                temporary_password=password,
            ),
        )

    def _build_welcome_email(self, full_name: str, email: str, temporary_password: str) -> str:
        safe_full_name = escape(full_name)
        safe_email = escape(email)
        safe_password = escape(temporary_password)

        return f"""
        <div style="font-family:Arial,sans-serif;color:#0f172a;line-height:1.6;background:#f5f9ff;padding:24px">
            <div style="max-width:640px;margin:auto;background:#ffffff;border-radius:18px;padding:28px;border:1px solid #dbeafe">
                <p style="margin:0;color:#0072CE;font-weight:700;letter-spacing:2px">BIOPARK UCE</p>
                <h2 style="color:#0f172a;margin:12px 0 8px">Bienvenido al parqueadero inteligente</h2>
                <p>Hola {safe_full_name},</p>
                <p>Tu suscripcion anual ha sido registrada correctamente.</p>
                <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:12px;padding:16px;margin:18px 0">
                    <p style="margin:0 0 8px"><strong>Usuario:</strong> {safe_email}</p>
                    <p style="margin:0"><strong>Contrasena temporal:</strong> {safe_password}</p>
                </div>
                <p>Usa estas credenciales para ingresar al sistema. Por seguridad, cambia tu contrasena en el primer inicio de sesion.</p>
                <p style="color:#64748b;font-size:13px;margin-top:24px">Universidad Central del Ecuador - BIOPARK</p>
            </div>
        </div>
        """
