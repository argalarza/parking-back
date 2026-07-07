import os
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.modules.auth.adapters.outbound.persistence.postgres_repository import (
    SqlAlchemyAuthRepository,
)
from app.modules.auth.application.use_cases import (
    AdminLoginUseCase,
    ChangePasswordUseCase,
    PersonLoginUseCase,
)


JWT_ALGORITHM = "HS256"
security = HTTPBearer(auto_error=False)


def get_jwt_secret_key() -> str:
    return os.getenv("JWT_SECRET_KEY", "change-me-in-production")


def get_jwt_expire_minutes() -> int:
    return int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


def get_admin_login_use_case(db: Session = Depends(get_db)) -> AdminLoginUseCase:
    return AdminLoginUseCase(
        repository=SqlAlchemyAuthRepository(db),
        secret_key=get_jwt_secret_key(),
        algorithm=JWT_ALGORITHM,
        access_token_expire_minutes=get_jwt_expire_minutes(),
    )


def get_person_login_use_case(db: Session = Depends(get_db)) -> PersonLoginUseCase:
    return PersonLoginUseCase(
        repository=SqlAlchemyAuthRepository(db),
        secret_key=get_jwt_secret_key(),
        algorithm=JWT_ALGORITHM,
        access_token_expire_minutes=get_jwt_expire_minutes(),
    )


def get_change_password_use_case(db: Session = Depends(get_db)) -> ChangePasswordUseCase:
    return ChangePasswordUseCase(repository=SqlAlchemyAuthRepository(db))


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> dict:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="No autenticado.")

    try:
        payload = jwt.decode(
            credentials.credentials,
            get_jwt_secret_key(),
            algorithms=[JWT_ALGORITHM],
        )
        user_id = payload.get("id")
        user_type = payload.get("type")
        if user_id is None or user_type not in {"admin", "person"}:
            raise HTTPException(status_code=401, detail="Token invalido.")

        repository = SqlAlchemyAuthRepository(db)
        subject_id = UUID(str(user_id))

        if user_type == "admin":
            current_user = repository.get_admin_by_id(subject_id)
        else:
            current_user = repository.get_person_by_id(subject_id)
            if current_user is not None and not current_user["is_active"]:
                raise HTTPException(status_code=403, detail="El usuario se encuentra inactivo.")

        if current_user is None:
            raise HTTPException(status_code=401, detail="Usuario no encontrado.")

        current_user["type"] = user_type
        return current_user
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Token invalido.") from exc
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Token invalido.") from exc


def get_current_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user["type"] != "admin":
        raise HTTPException(status_code=403, detail="Se requieren permisos de administrador.")
    return current_user
