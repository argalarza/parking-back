from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.modules.gates.adapters.outbound.persistence.postgres_repository import (
    SqlAlchemyGateRepository,
)
from app.modules.gates.application.use_cases import (
    CreateGateUseCase,
    DeleteGateUseCase,
    GetGateUseCase,
    ListGatesUseCase,
    UpdateGateUseCase,
)


def get_list_gates_use_case(db: Session = Depends(get_db)) -> ListGatesUseCase:
    return ListGatesUseCase(repository=SqlAlchemyGateRepository(db))


def get_gate_use_case(db: Session = Depends(get_db)) -> GetGateUseCase:
    return GetGateUseCase(repository=SqlAlchemyGateRepository(db))


def get_create_gate_use_case(db: Session = Depends(get_db)) -> CreateGateUseCase:
    return CreateGateUseCase(repository=SqlAlchemyGateRepository(db))


def get_update_gate_use_case(db: Session = Depends(get_db)) -> UpdateGateUseCase:
    return UpdateGateUseCase(repository=SqlAlchemyGateRepository(db))


def get_delete_gate_use_case(db: Session = Depends(get_db)) -> DeleteGateUseCase:
    return DeleteGateUseCase(repository=SqlAlchemyGateRepository(db))
