from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.application.errors import ConflictError, NotFoundError, RepositoryError
from app.modules.admin_users.adapters.inbound.http.schemas import (
    AdminUserCreateRequest,
    AdminUserCreateResponse,
    AdminUserMutationResponse,
    AdminUserResponse,
    AdminUserStatusRequest,
)
from app.modules.admin_users.application.use_cases import (
    CreateAdminUserUseCase,
    GetAdminUserUseCase,
    ListAdminUsersUseCase,
    SetAdminUserActiveUseCase,
)
from app.modules.admin_users.dependencies import (
    get_create_admin_user_use_case,
    get_get_admin_user_use_case,
    get_list_admin_users_use_case,
    get_set_admin_user_active_use_case,
    require_admin_user_manager,
)


router = APIRouter(
    prefix="/admin/users",
    tags=["usuarios administrativos"],
    dependencies=[Depends(require_admin_user_manager)],
)


@router.get("", response_model=list[AdminUserResponse])
def list_admin_users(
    use_case: ListAdminUsersUseCase = Depends(get_list_admin_users_use_case),
) -> list[dict]:
    try:
        return use_case.execute()
    except RepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{user_id}", response_model=AdminUserResponse)
def get_admin_user(
    user_id: UUID,
    use_case: GetAdminUserUseCase = Depends(get_get_admin_user_use_case),
) -> dict:
    try:
        return use_case.execute(user_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("", response_model=AdminUserCreateResponse)
def create_admin_user(
    payload: AdminUserCreateRequest,
    use_case: CreateAdminUserUseCase = Depends(get_create_admin_user_use_case),
) -> dict:
    try:
        return use_case.execute(
            username=payload.username,
            full_name=payload.full_name,
            email=str(payload.email),
            role=payload.role,
        )
    except ConflictError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.patch("/{user_id}/status", response_model=AdminUserMutationResponse)
def set_admin_user_status(
    user_id: UUID,
    payload: AdminUserStatusRequest,
    use_case: SetAdminUserActiveUseCase = Depends(get_set_admin_user_active_use_case),
) -> dict:
    try:
        return use_case.execute(user_id=user_id, is_active=payload.is_active)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
