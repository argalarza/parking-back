from uuid import UUID

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.application.errors import RepositoryError


class SqlAlchemyAuthRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_admin_by_username(self, username: str) -> dict | None:
        try:
            result = self._db.execute(
                text(
                    """
                    SELECT id, username, password_hash
                    FROM public.users
                    WHERE username = :username
                    LIMIT 1
                    """
                ),
                {"username": username},
            )
            row = result.mappings().first()
            return dict(row) if row else None
        except SQLAlchemyError as exc:
            raise RepositoryError("Error al consultar el administrador.") from exc

    def get_person_by_email(self, email: str) -> dict | None:
        try:
            result = self._db.execute(
                text(
                    """
                    SELECT id, email, password_hash, is_active, must_change_password
                    FROM uce.core_persons
                    WHERE email = :email
                    LIMIT 1
                    """
                ),
                {"email": email},
            )
            row = result.mappings().first()
            return dict(row) if row else None
        except SQLAlchemyError as exc:
            raise RepositoryError("Error al consultar el usuario del parqueadero.") from exc

    def get_admin_by_id(self, admin_id: UUID) -> dict | None:
        try:
            result = self._db.execute(
                text(
                    """
                    SELECT id, username
                    FROM public.users
                    WHERE id = :admin_id
                    LIMIT 1
                    """
                ),
                {"admin_id": str(admin_id)},
            )
            row = result.mappings().first()
            return dict(row) if row else None
        except SQLAlchemyError as exc:
            raise RepositoryError("Error al consultar el administrador autenticado.") from exc

    def get_person_by_id(self, person_id: UUID) -> dict | None:
        try:
            result = self._db.execute(
                text(
                    """
                    SELECT id, email, is_active, must_change_password
                    FROM uce.core_persons
                    WHERE id = :person_id
                    LIMIT 1
                    """
                ),
                {"person_id": str(person_id)},
            )
            row = result.mappings().first()
            return dict(row) if row else None
        except SQLAlchemyError as exc:
            raise RepositoryError("Error al consultar el usuario autenticado.") from exc

    def get_person_password_hash_by_id(self, person_id: UUID) -> str | None:
        try:
            result = self._db.execute(
                text(
                    """
                    SELECT password_hash
                    FROM uce.core_persons
                    WHERE id = :person_id
                    LIMIT 1
                    """
                ),
                {"person_id": str(person_id)},
            )
            row = result.mappings().first()
            return str(row["password_hash"]) if row else None
        except SQLAlchemyError as exc:
            raise RepositoryError("Error al consultar la contrasena del usuario autenticado.") from exc

    def update_person_password(self, person_id: UUID, password_hash: str) -> None:
        try:
            self._db.execute(
                text(
                    """
                    UPDATE uce.core_persons
                    SET password_hash = :password_hash,
                        must_change_password = false
                    WHERE id = :person_id
                    """
                ),
                {"person_id": str(person_id), "password_hash": password_hash},
            )
            self._db.commit()
        except SQLAlchemyError as exc:
            self._db.rollback()
            raise RepositoryError("Error al actualizar la contrasena del usuario.") from exc
