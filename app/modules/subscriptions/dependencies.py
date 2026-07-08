import os
from decimal import Decimal, InvalidOperation
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.modules.notifications.adapters.outbound.email.smtp_email_sender import SmtpEmailSender
from app.modules.subscriptions.adapters.outbound.notification.email_notifier import SubscriberEmailNotifier
from app.modules.auth.dependencies import get_current_user
from app.modules.subscriptions.adapters.outbound.persistence.postgres_repository import (
    SqlAlchemySubscriptionRepository,
)
from app.modules.subscriptions.adapters.outbound.storage.file_storage import LocalReceiptStorage
from app.modules.subscriptions.application.use_cases import RegisterSubscriberUseCase
from app.modules.subscriptions.application.use_cases import GetMySubscriptionUseCase, ListSubscribersUseCase


def get_subscription_annual_amount() -> Decimal:
    try:
        return Decimal(os.getenv("SUBSCRIPTION_ANNUAL_AMOUNT", "0"))
    except InvalidOperation as exc:
        raise HTTPException(status_code=500, detail="Monto anual de suscripcion invalido.") from exc


def get_receipt_max_size_bytes() -> int:
    return int(os.getenv("SUBSCRIPTION_RECEIPT_MAX_BYTES", str(5 * 1024 * 1024)))


def get_register_subscriber_use_case(db: Session = Depends(get_db)) -> RegisterSubscriberUseCase:
    return RegisterSubscriberUseCase(
        repository=SqlAlchemySubscriptionRepository(db),
        receipt_storage=LocalReceiptStorage(max_size_bytes=get_receipt_max_size_bytes()),
        notifier=SubscriberEmailNotifier(email_sender=SmtpEmailSender()),
        annual_amount=get_subscription_annual_amount(),
    )


def get_my_subscription_use_case(db: Session = Depends(get_db)) -> GetMySubscriptionUseCase:
    return GetMySubscriptionUseCase(repository=SqlAlchemySubscriptionRepository(db))


def get_list_subscribers_use_case(db: Session = Depends(get_db)) -> ListSubscribersUseCase:
    return ListSubscribersUseCase(repository=SqlAlchemySubscriptionRepository(db))


def get_current_subscriber(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user["type"] != "person":
        raise HTTPException(status_code=403, detail="Esta vista es solo para suscriptores.")
    current_user["id"] = UUID(str(current_user["id"]))
    return current_user


def get_subscription_validator(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    if current_user["type"] != "admin":
        raise HTTPException(status_code=403, detail="Se requiere rol asesor o admin_ti.")

    try:
        result = db.execute(
            text(
                """
                SELECT role
                FROM public.users
                WHERE id = :user_id
                LIMIT 1
                """
            ),
            {"user_id": str(current_user["id"])},
        )
        role = result.scalar_one_or_none()
    except (SQLAlchemyError, ValueError) as exc:
        raise HTTPException(status_code=500, detail="Error al validar el rol del usuario.") from exc

    if role not in {"asesor", "admin_ti", "admin"}:
        raise HTTPException(status_code=403, detail="Se requiere rol asesor o admin_ti.")

    current_user["id"] = UUID(str(current_user["id"]))
    current_user["role"] = role
    return current_user
