from datetime import date
from decimal import Decimal
from secrets import token_urlsafe
from uuid import UUID

from app.application.errors import ConflictError, RepositoryError, ValidationError
from app.modules.auth.application.use_cases import pwd_context
from app.modules.subscriptions.application.ports import (
    ReceiptStorage,
    SubscriberNotificationPort,
    SubscriptionRepository,
)


class NoopSubscriberNotificationPort:
    def send_initial_credentials(self, full_name: str, email: str, password: str) -> None:
        return None


class RegisterSubscriberUseCase:
    def __init__(
        self,
        repository: SubscriptionRepository,
        receipt_storage: ReceiptStorage,
        notifier: SubscriberNotificationPort | None = None,
        annual_amount: Decimal = Decimal("0"),
    ) -> None:
        self._repository = repository
        self._receipt_storage = receipt_storage
        self._notifier = notifier or NoopSubscriberNotificationPort()
        self._annual_amount = annual_amount

    def execute(
        self,
        first_names: str,
        last_names: str,
        email: str,
        phone: str,
        dni: str,
        receipt_filename: str,
        receipt_content_type: str | None,
        receipt_file,
        validated_by: UUID,
    ) -> dict:
        valid_from = date.today()
        valid_until = self._add_one_year(valid_from)
        temporary_password = token_urlsafe(12)
        password_hash = pwd_context.hash(temporary_password)
        receipt_path = self._receipt_storage.save(
            filename=receipt_filename,
            content_type=receipt_content_type,
            file=receipt_file,
        )

        try:
            person_id = self._repository.create_subscriber_with_payment(
                dni=dni,
                first_names=first_names,
                last_names=last_names,
                phone=phone,
                email=email,
                password_hash=password_hash,
                valid_from=valid_from,
                valid_until=valid_until,
                receipt_path=receipt_path,
                validated_by=validated_by,
                amount=self._annual_amount,
            )
        except (ConflictError, RepositoryError, ValidationError):
            self._receipt_storage.delete(receipt_path)
            raise

        email_sent = True
        email_message = "Correo de bienvenida enviado."
        try:
            self._notifier.send_initial_credentials(
                full_name=f"{first_names} {last_names}",
                email=email,
                password=temporary_password,
            )
        except RepositoryError as exc:
            email_sent = False
            email_message = str(exc)

        return {
            "success": True,
            "message": "Suscriptor registrado y pago validado.",
            "person_id": person_id,
            "email_sent": email_sent,
            "email_message": email_message,
        }

    def _add_one_year(self, value: date) -> date:
        try:
            return value.replace(year=value.year + 1)
        except ValueError:
            return value.replace(month=2, day=28, year=value.year + 1)


class GetMySubscriptionUseCase:
    def __init__(self, repository: SubscriptionRepository) -> None:
        self._repository = repository

    def execute(self, person_id: UUID) -> dict:
        summary = self._repository.get_subscriber_summary(person_id)
        if summary is None:
            raise RepositoryError("No se encontro la informacion del suscriptor.")

        valid_from = summary.get("valid_from")
        valid_until = summary.get("valid_until")
        status = summary.get("status")
        is_active = (
            status == "VALIDADO"
            and valid_from is not None
            and valid_until is not None
            and valid_from <= date.today() <= valid_until
        )

        summary["is_active"] = is_active
        return summary


class ListSubscribersUseCase:
    def __init__(self, repository: SubscriptionRepository) -> None:
        self._repository = repository

    def execute(self) -> list[dict]:
        subscribers = self._repository.list_subscribers()
        today = date.today()

        for subscriber in subscribers:
            valid_from = subscriber.get("valid_from")
            valid_until = subscriber.get("valid_until")
            status = subscriber.get("status")
            subscriber["subscription_active"] = (
                status == "VALIDADO"
                and valid_from is not None
                and valid_until is not None
                and valid_from <= today <= valid_until
            )

        return subscribers
