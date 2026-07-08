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
                {
                    "plate": plate,
                    "brand": brand,
                    "model": model,
                },
            )

            vehicle_id = result.scalar_one()

            self._db.commit()

            return vehicle_id

        except IntegrityError as exc:
            self._db.rollback()

            # Muestra el error REAL de PostgreSQL en la terminal
            print("\n========== ERROR INTEGRITY VEHICULO ==========")
            print(repr(exc))
            print("ERROR ORIGINAL:")
            print(exc.orig)
            print("==============================================\n")

            raise ConflictError(
                f"La placa ya existe o viola una restriccion. Error: {exc.orig}"
            ) from exc

        except SQLAlchemyError as exc:
            self._db.rollback()

            # Muestra el error REAL de SQLAlchemy/PostgreSQL
            print("\n========== ERROR SQL VEHICULO ==========")
            print(repr(exc))
            print("ERROR ORIGINAL:")

            if hasattr(exc, "orig"):
                print(exc.orig)
            else:
                print(exc)

            print("========================================\n")

            raise RepositoryError(
                f"Error al crear el vehiculo: {exc}"
            ) from exc

        except Exception as exc:
            self._db.rollback()

            # Captura cualquier otro error inesperado
            import traceback

            print("\n========== ERROR INESPERADO VEHICULO ==========")
            traceback.print_exc()
            print("================================================\n")

            raise RepositoryError(
                f"Error inesperado al crear el vehiculo: {exc}"
            ) from exc

    def link_vehicle_person(
        self,
        vehicle_id: UUID,
        person_id: UUID,
        relation: str,
    ) -> None:
        try:
            self._db.execute(
                text(
                    """
                    INSERT INTO uce.vehicle_persons
                    (vehicle_id, person_id, relation)
                    VALUES (:vehicle_id, :person_id, :relation)
                    """
                ),
                {
                    "vehicle_id": str(vehicle_id),
                    "person_id": str(person_id),
                    "relation": relation,
                },
            )

            self._db.commit()

        except IntegrityError as exc:
            self._db.rollback()

            print("\n========== ERROR INTEGRITY VINCULO ==========")
            print(repr(exc))
            print("ERROR ORIGINAL:")
            print(exc.orig)
            print("=============================================\n")

            raise ConflictError(
                f"No se pudo crear el vinculo. Error: {exc.orig}"
            ) from exc

        except SQLAlchemyError as exc:
            self._db.rollback()

            print("\n========== ERROR SQL VINCULO ==========")
            print(repr(exc))

            if hasattr(exc, "orig"):
                print(exc.orig)

            print("=======================================\n")

            raise RepositoryError(
                f"Error al crear el vinculo: {exc}"
            ) from exc