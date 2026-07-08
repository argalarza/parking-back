from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.application.errors import ConflictError, RepositoryError, ValidationError
from app.modules.subscriptions.adapters.inbound.http.schemas import (
    MySubscriptionResponse,
    SubscriberListItem,
    SubscriberRegistrationForm,
    SubscriberRegistrationResponse,
)
from app.modules.subscriptions.application.use_cases import (
    GetMySubscriptionUseCase,
    ListSubscribersUseCase,
    RegisterSubscriberUseCase,
)
from app.modules.subscriptions.dependencies import (
    get_current_subscriber,
    get_list_subscribers_use_case,
    get_my_subscription_use_case,
    get_register_subscriber_use_case,
    get_subscription_validator,
)


router = APIRouter(prefix="/suscripciones", tags=["suscripciones"])


@router.get("", response_model=list[SubscriberListItem])
def list_subscribers(
    current_user: dict = Depends(get_subscription_validator),
    use_case: ListSubscribersUseCase = Depends(get_list_subscribers_use_case),
) -> list[dict]:
    try:
        return use_case.execute()
    except RepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/me", response_model=MySubscriptionResponse)
def get_my_subscription(
    current_user: dict = Depends(get_current_subscriber),
    use_case: GetMySubscriptionUseCase = Depends(get_my_subscription_use_case),
) -> dict:
    try:
        return use_case.execute(person_id=current_user["id"])
    except RepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("", response_model=SubscriberRegistrationResponse)
def register_subscriber(
    payload: Annotated[SubscriberRegistrationForm, Depends(SubscriberRegistrationForm.as_form)],
    receipt: Annotated[UploadFile, File(...)],
    current_user: dict = Depends(get_subscription_validator),
    use_case: RegisterSubscriberUseCase = Depends(get_register_subscriber_use_case),
) -> dict:
    try:
        return use_case.execute(
            first_names=payload.first_names,
            last_names=payload.last_names,
            email=str(payload.email),
            phone=payload.phone,
            dni=payload.dni,
            receipt_filename=receipt.filename or "",
            receipt_content_type=receipt.content_type,
            receipt_file=receipt.file,
            validated_by=current_user["id"],
        )
    except (ConflictError, ValidationError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
