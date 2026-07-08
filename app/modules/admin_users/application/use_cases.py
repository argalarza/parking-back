from secrets import token_urlsafe
from uuid import UUID

from app.application.errors import NotFoundError, RepositoryError
from app.modules.admin_users.application.ports import AdminUserRepository
from app.modules.auth.application.use_cases import pwd_context
from app.modules.notifications.application.ports import EmailSender


class ListAdminUsersUseCase:
    def __init__(self, repository: AdminUserRepository) -> None:
        self._repository = repository

    def execute(self) -> list[dict]:
        return self._repository.list_admin_users()


class GetAdminUserUseCase:
    def __init__(self, repository: AdminUserRepository) -> None:
        self._repository = repository

    def execute(self, user_id: UUID) -> dict:
        user = self._repository.get_admin_user_by_id(user_id)
        if user is None:
            raise NotFoundError("Usuario administrativo no encontrado.")
        return user


class CreateAdminUserUseCase:
    def __init__(self, repository: AdminUserRepository, email_sender: EmailSender) -> None:
        self._repository = repository
        self._email_sender = email_sender

    def execute(self, username: str, full_name: str, email: str, role: str) -> dict:
        temporary_password = token_urlsafe(10)
        password_hash = pwd_context.hash(temporary_password)
        user_id = self._repository.create_admin_user(
            username=username,
            full_name=full_name,
            email=email,
            role=role,
            password_hash=password_hash,
        )

        email_sent = True
        email_message = "Correo de bienvenida enviado."
        try:
            self._email_sender.send_email(
                to=email,
                subject="Bienvenido a UPark",
                html=self._build_welcome_email(
                    full_name=full_name,
                    username=username,
                    temporary_password=temporary_password,
                ),
            )
        except RepositoryError as exc:
            email_sent = False
            email_message = str(exc)

        return {
            "success": True,
            "message": "Usuario administrativo creado correctamente.",
            "id": user_id,
            "email_sent": email_sent,
            "email_message": email_message,
        }

    def _build_welcome_email(self, full_name: str, username: str, temporary_password: str) -> str:
        return f"""
        <div style="font-family:Arial,sans-serif;color:#0f172a;line-height:1.6">
            <h2 style="color:#1e3a8a">Bienvenido a UPark</h2>
            <p>Hola {full_name},</p>
            <p>Tu cuenta administrativa ha sido creada.</p>
            <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:12px;padding:16px">
                <p><strong>Usuario:</strong> {username}</p>
                <p><strong>Contrasena temporal:</strong> {temporary_password}</p>
            </div>
            <p>Ingresa al sistema y cambia tu contrasena en el primer inicio de sesion.</p>
        </div>
        """


class SetAdminUserActiveUseCase:
    def __init__(self, repository: AdminUserRepository) -> None:
        self._repository = repository

    def execute(self, user_id: UUID, is_active: bool) -> dict:
        updated = self._repository.set_admin_active(user_id=user_id, is_active=is_active)
        if not updated:
            raise NotFoundError("Usuario administrativo no encontrado.")
        return {
            "success": True,
            "message": "Estado del usuario administrativo actualizado correctamente.",
        }
