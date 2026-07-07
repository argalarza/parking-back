from fastapi import APIRouter, Depends, HTTPException

from app.application.errors import ConflictError, RepositoryError
from app.modules.guests.adapters.inbound.http.schemas import (
    GuestRegisterRequest,
    GuestRegisterResponse,
)
from app.modules.guests.application.use_cases import RegisterGuestUseCase
from app.modules.guests.dependencies import get_register_guest_use_case


router = APIRouter(prefix="/visitantes", tags=["visitantes"])


@router.post("/registro", response_model=GuestRegisterResponse)
def register_guest(
    payload: GuestRegisterRequest,
    use_case: RegisterGuestUseCase = Depends(get_register_guest_use_case),
) -> dict:
    try:
        return use_case.execute(
            first_names=payload.first_names,
            last_names=payload.last_names,
            dni_type=payload.dni_type,
            dni=payload.dni,
            phone=payload.phone,
            email=str(payload.email),
            fingerprint_code=payload.fingerprint_code,
            password=payload.password,
        )
    except ConflictError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
