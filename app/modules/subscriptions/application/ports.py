from datetime import date
from decimal import Decimal
from typing import BinaryIO, Protocol
from uuid import UUID


class SubscriptionRepository(Protocol):
    def create_subscriber_with_payment(
        self,
        dni: str,
        first_names: str,
        last_names: str,
        phone: str,
        email: str,
        password_hash: str,
        valid_from: date,
        valid_until: date,
        receipt_path: str,
        validated_by: UUID,
        amount: Decimal,
    ) -> UUID: ...

    def has_valid_subscription(self, person_id: UUID) -> bool: ...

    def get_subscriber_summary(self, person_id: UUID) -> dict | None: ...

    def list_subscribers(self) -> list[dict]: ...


class ReceiptStorage(Protocol):
    def save(self, filename: str, content_type: str | None, file: BinaryIO) -> str: ...

    def delete(self, path: str) -> None: ...


class SubscriberNotificationPort(Protocol):
    def send_initial_credentials(self, full_name: str, email: str, password: str) -> None: ...
