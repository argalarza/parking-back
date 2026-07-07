from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.modules.guests.adapters.outbound.persistence.postgres_repository import (
    SqlAlchemyGuestRepository,
)
from app.modules.guests.application.use_cases import RegisterGuestUseCase


def get_register_guest_use_case(db: Session = Depends(get_db)) -> RegisterGuestUseCase:
    return RegisterGuestUseCase(repository=SqlAlchemyGuestRepository(db))
