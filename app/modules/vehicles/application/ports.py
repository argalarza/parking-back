from typing import Protocol
from uuid import UUID


class VehicleRepository(Protocol):
    def create_vehicle(self, plate: str, brand: str, model: str) -> UUID: ...

    def link_vehicle_person(self, vehicle_id: UUID, person_id: UUID, relation: str) -> None: ...
