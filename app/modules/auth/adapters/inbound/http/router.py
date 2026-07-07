from fastapi import APIRouter, Depends, HTTPException

from app.application.errors import RepositoryError
from app.modules.auth.adapters.inbound.http.schemas import (
    AdminLoginRequest,
    ChangePasswordRequest,
    PersonLoginRequest,
    PersonLoginResponse,
    SuccessResponse,
    TokenResponse,
)
from app.modules.auth.application.use_cases import (
    AdminLoginUseCase,
    ChangePasswordUseCase,
    ForbiddenError,
    InvalidPasswordError,
    PersonLoginUseCase,
    UnauthorizedError,
)
from app.modules.auth.dependencies import (
    get_change_password_use_case,
    get_current_user,
    get_admin_login_use_case,
    get_person_login_use_case,
)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/admin/login", response_model=TokenResponse)
def admin_login(
    payload: AdminLoginRequest,
    use_case: AdminLoginUseCase = Depends(get_admin_login_use_case),
) -> dict:
    try:
        return use_case.execute(username=payload.username, password=payload.password)
    except UnauthorizedError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except RepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/login", response_model=PersonLoginResponse)
def person_login(
    payload: PersonLoginRequest,
    use_case: PersonLoginUseCase = Depends(get_person_login_use_case),
) -> dict:
    try:
        return use_case.execute(email=payload.email, password=payload.password)
    except UnauthorizedError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except ForbiddenError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except RepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/change-password", response_model=SuccessResponse)
def change_password(
    payload: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    use_case: ChangePasswordUseCase = Depends(get_change_password_use_case),
) -> dict:
    if current_user["type"] != "person":
        raise HTTPException(status_code=403, detail="Solo aplica a usuarios del parqueadero.")

    try:
        return use_case.execute(
            person_id=current_user["id"],
            current_password=payload.current_password,
            new_password=payload.new_password,
        )
    except InvalidPasswordError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
