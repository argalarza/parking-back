from uuid import UUID

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.application.errors import RepositoryError


class SqlAlchemyGateRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_gates(self) -> list[dict]:
        try:
            result = self._db.execute(
                text(
                    """
                    SELECT id, number, main_street, secondary_street, reference
                    FROM uce.gates
                    ORDER BY number NULLS LAST, reference
                    """
                )
            )
            return [dict(row._mapping) for row in result]
        except SQLAlchemyError as exc:
            raise RepositoryError("Error al listar las puertas.") from exc

    def get_gate_by_id(self, gate_id: UUID) -> dict | None:
        try:
            result = self._db.execute(
                text(
                    """
                    SELECT id, number, main_street, secondary_street, reference
                    FROM uce.gates
                    WHERE id = :gate_id
                    """
                ),
                {"gate_id": gate_id},
            )
            row = result.mappings().first()
            return dict(row) if row is not None else None
        except SQLAlchemyError as exc:
            raise RepositoryError("Error al obtener la puerta.") from exc

    def create_gate(
        self,
        number: int | None,
        main_street: str,
        secondary_street: str | None,
        reference: str,
    ) -> UUID:
        try:
            result = self._db.execute(
                text(
                    """
                    INSERT INTO uce.gates (number, main_street, secondary_street, reference)
                    VALUES (:number, :main_street, :secondary_street, :reference)
                    RETURNING id
                    """
                ),
                {
                    "number": number,
                    "main_street": main_street,
                    "secondary_street": secondary_street,
                    "reference": reference,
                },
            )
            gate_id = result.scalar_one()
            self._db.commit()
            return gate_id
        except SQLAlchemyError as exc:
            self._db.rollback()
            raise RepositoryError("Error al crear la puerta.") from exc

    def update_gate(
        self,
        gate_id: UUID,
        number: int | None,
        main_street: str,
        secondary_street: str | None,
        reference: str,
    ) -> bool:
        try:
            result = self._db.execute(
                text(
                    """
                    UPDATE uce.gates
                    SET number = :number,
                        main_street = :main_street,
                        secondary_street = :secondary_street,
                        reference = :reference
                    WHERE id = :gate_id
                    """
                ),
                {
                    "gate_id": gate_id,
                    "number": number,
                    "main_street": main_street,
                    "secondary_street": secondary_street,
                    "reference": reference,
                },
            )
            self._db.commit()
            return result.rowcount > 0
        except SQLAlchemyError as exc:
            self._db.rollback()
            raise RepositoryError("Error al actualizar la puerta.") from exc

    def delete_gate(self, gate_id: UUID) -> bool:
        try:
            result = self._db.execute(
                text(
                    """
                    DELETE FROM uce.gates
                    WHERE id = :gate_id
                    """
                ),
                {"gate_id": gate_id},
            )
            self._db.commit()
            return result.rowcount > 0
        except SQLAlchemyError as exc:
            self._db.rollback()
            raise RepositoryError("Error al eliminar la puerta.") from exc
