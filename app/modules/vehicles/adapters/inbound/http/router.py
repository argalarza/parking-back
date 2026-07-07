from fastapi import APIRouter, Depends, HTTPException

from app.application.errors import ConflictError, RepositoryError, ValidationError
from app.modules.vehicles.adapters.inbound.http.schemas import (
    VehicleCreateRequest,
    VehiclePersonLinkRequest,
)
from app.modules.vehicles.application.use_cases import (
    CreateVehicleUseCase,
    LinkVehiclePersonUseCase,
)
from app.modules.vehicles.dependencies import (
    get_create_vehicle_use_case,
    get_link_vehicle_person_use_case,
)


router = APIRouter(prefix="/gestion", tags=["vehiculos"])


@router.post("/vehiculo")
def create_vehicle(
    payload: VehicleCreateRequest,
    use_case: CreateVehicleUseCase = Depends(get_create_vehicle_use_case),
) -> dict:
    try:
        return use_case.execute(
            plate=payload.plate,
            brand=payload.brand,
            model=payload.model,
        )
    except ConflictError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/vincular")
def link_vehicle_person(
    payload: VehiclePersonLinkRequest,
    use_case: LinkVehiclePersonUseCase = Depends(get_link_vehicle_person_use_case),
) -> dict:
    try:
        return use_case.execute(
            vehicle_id=payload.vehicle_id,
            person_id=payload.person_id,
            relation=payload.relation,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
