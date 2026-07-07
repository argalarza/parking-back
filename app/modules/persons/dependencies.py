from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.modules.persons.adapters.outbound.persistence.postgres_repository import (
    SqlAlchemyPersonRepository,
)
from app.modules.persons.application.use_cases import CreatePersonUseCase


def get_create_person_use_case(db: Session = Depends(get_db)) -> CreatePersonUseCase:
    return CreatePersonUseCase(repository=SqlAlchemyPersonRepository(db))
