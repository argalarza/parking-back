from uuid import UUID

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.application.errors import ConflictError, RepositoryError


class SqlAlchemyGuestRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def register_guest(
        self,
        dni: str,
        dni_type: str,
        first_names: str,
        last_names: str,
        phone: str,
        email: str,
        fingerprint_code: str | None,
        password_hash: str,
    ) -> UUID:
        try:
            result = self._db.execute(
                text(
                    """
                    INSERT INTO uce.core_persons (
                        dni,
                        dni_type,
                        first_names,
                        last_names,
                        name,
                        phone,
                        email,
                        fingerprint_code,
                        password_hash,
                        person_type,
                        must_change_password
                    )
                    VALUES (
                        :dni,
                        :dni_type,
                        :first_names,
                        :last_names,
                        :name,
                        :phone,
                        :email,
                        :fingerprint_code,
                        :password_hash,
                        'VISITANTE',
                        false
                    )
                    RETURNING id
                    """
                ),
                {
                    "dni": dni,
                    "dni_type": dni_type,
                    "first_names": first_names,
                    "last_names": last_names,
                    "name": f"{first_names} {last_names}".strip(),
                    "phone": phone,
                    "email": email,
                    "fingerprint_code": fingerprint_code,
                    "password_hash": password_hash,
                },
            )
            person_id = result.scalar_one()
            self._db.commit()
            return person_id
        except IntegrityError as exc:
            self._db.rollback()
            raise ConflictError("El DNI o el correo ya existen.") from exc
        except SQLAlchemyError as exc:
            self._db.rollback()
            raise RepositoryError("Error al registrar el visitante.") from exc
