from fastapi import APIRouter, Depends, HTTPException

from app.application.errors import ConflictError, RepositoryError
from app.modules.persons.adapters.inbound.http.schemas import PersonCreateRequest
from app.modules.persons.application.use_cases import CreatePersonUseCase
from app.modules.persons.dependencies import get_create_person_use_case


router = APIRouter(prefix="/gestion/persona", tags=["personas"])


@router.post("")
def create_person(
    payload: PersonCreateRequest,
    use_case: CreatePersonUseCase = Depends(get_create_person_use_case),
) -> dict:
    try:
        return use_case.execute(
            dni=payload.dni,
            name=payload.name,
            last_names=payload.last_names,
        )
    except ConflictError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
