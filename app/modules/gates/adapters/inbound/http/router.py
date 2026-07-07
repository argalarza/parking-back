from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.application.errors import NotFoundError, RepositoryError
from app.modules.auth.dependencies import get_current_user
from app.modules.gates.adapters.inbound.http.schemas import (
    GateCreateRequest,
    GateMutationResponse,
    GateResponse,
    GateUpdateRequest,
)
from app.modules.gates.application.use_cases import (
    CreateGateUseCase,
    DeleteGateUseCase,
    GetGateUseCase,
    ListGatesUseCase,
    UpdateGateUseCase,
)
from app.modules.gates.dependencies import (
    get_create_gate_use_case,
    get_delete_gate_use_case,
    get_gate_use_case,
    get_list_gates_use_case,
    get_update_gate_use_case,
)


router = APIRouter(
    prefix="/puertas",
    tags=["puertas"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[GateResponse])
def list_gates(
    use_case: ListGatesUseCase = Depends(get_list_gates_use_case),
) -> list[dict]:
    try:
        return use_case.execute()
    except RepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{gate_id}", response_model=GateResponse)
def get_gate(
    gate_id: UUID,
    use_case: GetGateUseCase = Depends(get_gate_use_case),
) -> dict:
    try:
        return use_case.execute(gate_id=gate_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("", response_model=GateMutationResponse)
def create_gate(
    payload: GateCreateRequest,
    use_case: CreateGateUseCase = Depends(get_create_gate_use_case),
) -> dict:
    try:
        return use_case.execute(
            number=payload.number,
            main_street=payload.main_street,
            secondary_street=payload.secondary_street,
            reference=payload.reference,
        )
    except RepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.put("/{gate_id}", response_model=GateMutationResponse)
def update_gate(
    gate_id: UUID,
    payload: GateUpdateRequest,
    use_case: UpdateGateUseCase = Depends(get_update_gate_use_case),
) -> dict:
    try:
        return use_case.execute(
            gate_id=gate_id,
            number=payload.number,
            main_street=payload.main_street,
            secondary_street=payload.secondary_street,
            reference=payload.reference,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/{gate_id}", response_model=GateMutationResponse)
def delete_gate(
    gate_id: UUID,
    use_case: DeleteGateUseCase = Depends(get_delete_gate_use_case),
) -> dict:
    try:
        return use_case.execute(gate_id=gate_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
