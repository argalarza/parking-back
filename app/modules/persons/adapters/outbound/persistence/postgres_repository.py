from uuid import UUID

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.application.errors import ConflictError, RepositoryError


class SqlAlchemyPersonRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create_person(self, dni: str, name: str, last_names: str) -> UUID:
        try:
            result = self._db.execute(
                text(
                    """
                    INSERT INTO uce.core_persons (dni, name, last_names)
                    VALUES (:dni, :name, :last_names)
                    RETURNING id
                    """
                ),
                {"dni": dni, "name": name, "last_names": last_names},
            )
            person_id = result.scalar_one()
            self._db.commit()
            return person_id
        except IntegrityError as exc:
            self._db.rollback()
            raise ConflictError("El DNI ya existe o viola una restriccion.") from exc
        except SQLAlchemyError as exc:
            self._db.rollback()
            raise RepositoryError("Error al crear la persona.") from exc
