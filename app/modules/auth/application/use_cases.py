from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import jwt
from passlib.context import CryptContext

from app.modules.auth.application.ports import AuthRepository


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UnauthorizedError(Exception):
    pass


class ForbiddenError(Exception):
    pass


class InvalidPasswordError(Exception):
    pass


class AdminLoginUseCase:
    def __init__(
        self,
        repository: AuthRepository,
        secret_key: str,
        algorithm: str,
        access_token_expire_minutes: int,
    ) -> None:
        self._repository = repository
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_token_expire_minutes = access_token_expire_minutes

    def execute(self, username: str, password: str) -> dict:
        admin = self._repository.get_admin_by_username(username)
        if admin is None or not pwd_context.verify(password, admin["password_hash"]):
            raise UnauthorizedError("Credenciales invalidas.")
        if not admin["is_active"]:
            raise ForbiddenError("El usuario administrativo se encuentra inactivo.")

        return {
            "access_token": self._create_access_token(
                subject_id=admin["id"],
                subject_type="admin",
                role=admin["role"],
            ),
            "token_type": "bearer",
            "must_change_password": bool(admin["must_change_password"]),
            "role": admin["role"],
        }

    def _create_access_token(self, subject_id: UUID, subject_type: str, role: str) -> str:
        expires_at = datetime.now(UTC) + timedelta(minutes=self._access_token_expire_minutes)
        payload = {
            "sub": str(subject_id),
            "id": str(subject_id),
            "type": subject_type,
            "role": role,
            "exp": expires_at,
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)


class PersonLoginUseCase:
    def __init__(
        self,
        repository: AuthRepository,
        secret_key: str,
        algorithm: str,
        access_token_expire_minutes: int,
    ) -> None:
        self._repository = repository
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_token_expire_minutes = access_token_expire_minutes

    def execute(self, email: str, password: str) -> dict:
        person = self._repository.get_person_by_email(email)
        if person is None or not pwd_context.verify(password, person["password_hash"]):
            raise UnauthorizedError("Credenciales invalidas.")
        if not person["is_active"]:
            raise ForbiddenError("El usuario se encuentra inactivo.")

        return {
            "access_token": self._create_access_token(subject_id=person["id"], subject_type="person"),
            "token_type": "bearer",
            "must_change_password": bool(person["must_change_password"]),
        }

    def _create_access_token(self, subject_id: UUID, subject_type: str) -> str:
        expires_at = datetime.now(UTC) + timedelta(minutes=self._access_token_expire_minutes)
        payload = {
            "sub": str(subject_id),
            "id": str(subject_id),
            "type": subject_type,
            "exp": expires_at,
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)


class ChangePasswordUseCase:
    def __init__(self, repository: AuthRepository) -> None:
        self._repository = repository

    def execute(self, user_id: UUID, user_type: str, current_password: str, new_password: str) -> dict:
        if user_type == "admin":
            password_hash = self._repository.get_admin_password_hash_by_id(user_id)
        else:
            password_hash = self._repository.get_person_password_hash_by_id(user_id)

        if password_hash is None or not pwd_context.verify(current_password, password_hash):
            raise InvalidPasswordError("La contrasena actual es incorrecta.")

        new_password_hash = pwd_context.hash(new_password)
        if user_type == "admin":
            self._repository.update_admin_password(admin_id=user_id, password_hash=new_password_hash)
        else:
            self._repository.update_person_password(person_id=user_id, password_hash=new_password_hash)
        return {
            "success": True,
            "message": "Contrasena actualizada correctamente.",
        }
