from uuid import UUID

from app.application.errors import ValidationError
from app.modules.vehicles.application.ports import VehicleRepository


class CreateVehicleUseCase:
    def __init__(self, repository: VehicleRepository) -> None:
        self._repository = repository

    def execute(self, plate: str, brand: str, model: str) -> dict:
        vehicle_id = self._repository.create_vehicle(plate=plate, brand=brand, model=model)
        return {
            "success": True,
            "message": "Vehiculo creado correctamente.",
            "id": vehicle_id,
        }


class LinkVehiclePersonUseCase:
    def __init__(self, repository: VehicleRepository) -> None:
        self._repository = repository

    def execute(self, vehicle_id: UUID, person_id: UUID, relation: str) -> dict:
        if relation not in {"DUENO", "AUTORIZADO"}:
            raise ValidationError("La relacion debe ser DUENO o AUTORIZADO.")

        self._repository.link_vehicle_person(
            vehicle_id=vehicle_id,
            person_id=person_id,
            relation=relation,
        )
        return {
            "success": True,
            "message": "Vinculo creado correctamente.",
        }
