from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.modules.admin_users.adapters.outbound.persistence.postgres_repository import (
    SqlAlchemyAdminUserRepository,
)
from app.modules.admin_users.application.use_cases import (
    CreateAdminUserUseCase,
    GetAdminUserUseCase,
    ListAdminUsersUseCase,
    SetAdminUserActiveUseCase,
)
from app.modules.auth.dependencies import get_current_user
from app.modules.notifications.adapters.outbound.email.smtp_email_sender import SmtpEmailSender


def require_admin_user_manager(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user["type"] != "admin":
        raise HTTPException(status_code=403, detail="Se requiere usuario administrativo.")
    if current_user.get("role") not in {"admin", "admin_ti"}:
        raise HTTPException(status_code=403, detail="Se requiere rol admin o admin_ti.")
    return current_user


def get_list_admin_users_use_case(db: Session = Depends(get_db)) -> ListAdminUsersUseCase:
    return ListAdminUsersUseCase(repository=SqlAlchemyAdminUserRepository(db))


def get_get_admin_user_use_case(db: Session = Depends(get_db)) -> GetAdminUserUseCase:
    return GetAdminUserUseCase(repository=SqlAlchemyAdminUserRepository(db))


def get_create_admin_user_use_case(db: Session = Depends(get_db)) -> CreateAdminUserUseCase:
    return CreateAdminUserUseCase(
        repository=SqlAlchemyAdminUserRepository(db),
        email_sender=SmtpEmailSender(),
    )


def get_set_admin_user_active_use_case(db: Session = Depends(get_db)) -> SetAdminUserActiveUseCase:
    return SetAdminUserActiveUseCase(repository=SqlAlchemyAdminUserRepository(db))
