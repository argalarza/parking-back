from uuid import UUID

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.application.errors import ConflictError, RepositoryError


class SqlAlchemyAdminUserRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_admin_users(self) -> list[dict]:
        try:
            result = self._db.execute(
                text(
                    """
                    SELECT
                        id,
                        username,
                        full_name,
                        email,
                        role,
                        is_active,
                        must_change_password,
                        created_date,
                        last_modified_date
                    FROM public.users
                    ORDER BY created_date DESC
                    """
                )
            )
            return [dict(row._mapping) for row in result]
        except SQLAlchemyError as exc:
            raise RepositoryError("Error al listar usuarios administrativos.") from exc

    def get_admin_user_by_id(self, user_id: UUID) -> dict | None:
        try:
            result = self._db.execute(
                text(
                    """
                    SELECT
                        id,
                        username,
                        full_name,
                        email,
                        role,
                        is_active,
                        must_change_password,
                        created_date,
                        last_modified_date
                    FROM public.users
                    WHERE id = :user_id
                    LIMIT 1
                    """
                ),
                {"user_id": str(user_id)},
            )
            row = result.mappings().first()
            return dict(row) if row else None
        except SQLAlchemyError as exc:
            raise RepositoryError("Error al consultar el usuario administrativo.") from exc

    def create_admin_user(
        self,
        username: str,
        full_name: str,
        email: str,
        role: str,
        password_hash: str,
    ) -> UUID:
        try:
            result = self._db.execute(
                text(
                    """
                    INSERT INTO public.users (
                        username,
                        full_name,
                        email,
                        role,
                        password_hash,
                        must_change_password,
                        is_active
                    )
                    VALUES (
                        :username,
                        :full_name,
                        :email,
                        :role,
                        :password_hash,
                        true,
                        true
                    )
                    RETURNING id
                    """
                ),
                {
                    "username": username,
                    "full_name": full_name,
                    "email": email,
                    "role": role,
                    "password_hash": password_hash,
                },
            )
            user_id = result.scalar_one()
            self._db.commit()
            return user_id
        except IntegrityError as exc:
            self._db.rollback()
            raise ConflictError("El username o correo ya existen.") from exc
        except SQLAlchemyError as exc:
            self._db.rollback()
            raise RepositoryError("Error al crear el usuario administrativo.") from exc

    def set_admin_active(self, user_id: UUID, is_active: bool) -> bool:
        try:
            result = self._db.execute(
                text(
                    """
                    UPDATE public.users
                    SET is_active = :is_active
                    WHERE id = :user_id
                    """
                ),
                {"user_id": str(user_id), "is_active": is_active},
            )
            self._db.commit()
            return result.rowcount > 0
        except SQLAlchemyError as exc:
            self._db.rollback()
            raise RepositoryError("Error al actualizar el estado del usuario administrativo.") from exc
