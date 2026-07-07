from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.modules.vehicles.adapters.outbound.persistence.postgres_repository import (
    SqlAlchemyVehicleRepository,
)
from app.modules.vehicles.application.use_cases import (
    CreateVehicleUseCase,
    LinkVehiclePersonUseCase,
)


def get_create_vehicle_use_case(db: Session = Depends(get_db)) -> CreateVehicleUseCase:
    repository = SqlAlchemyVehicleRepository(db)
    return CreateVehicleUseCase(repository=repository)


def get_link_vehicle_person_use_case(db: Session = Depends(get_db)) -> LinkVehiclePersonUseCase:
    repository = SqlAlchemyVehicleRepository(db)
    return LinkVehiclePersonUseCase(repository=repository)
