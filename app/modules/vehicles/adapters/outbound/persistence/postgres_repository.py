from uuid import UUID

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.application.errors import ConflictError, RepositoryError


class SqlAlchemyVehicleRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create_vehicle(self, plate: str, brand: str, model: str) -> UUID:
        try:
            result = self._db.execute(
                text(
                    """
                    INSERT INTO uce.core_vehicles (plate, brand, model)
                    VALUES (:plate, :brand, :model)
                    RETURNING id
                    """
                ),
                {"plate": plate, "brand": brand, "model": model},
            )
            vehicle_id = result.scalar_one()
            self._db.commit()
            return vehicle_id
        except IntegrityError as exc:
            self._db.rollback()
            raise ConflictError("La placa ya existe o viola una restriccion.") from exc
        except SQLAlchemyError as exc:
            self._db.rollback()
            raise RepositoryError("Error al crear el vehiculo.") from exc

    def link_vehicle_person(self, vehicle_id: UUID, person_id: UUID, relation: str) -> None:
        try:
            self._db.execute(
                text(
                    """
                    INSERT INTO uce.vehicle_persons (vehicle_id, person_id, relation)
                    VALUES (:vehicle_id, :person_id, :relation)
                    """
                ),
                {"vehicle_id": str(vehicle_id), "person_id": str(person_id), "relation": relation},
            )
            self._db.commit()
        except IntegrityError as exc:
            self._db.rollback()
            raise ConflictError("No se pudo crear el vinculo por datos duplicados o invalidos.") from exc
        except SQLAlchemyError as exc:
            self._db.rollback()
            raise RepositoryError("Error al crear el vinculo.") from exc
