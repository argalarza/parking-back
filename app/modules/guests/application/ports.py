from typing import Protocol
from uuid import UUID


class GuestRepository(Protocol):
    def register_guest(
        self,
        dni: str,
        dni_type: str,
        first_names: str,
        last_names: str,
        phone: str,
        email: str,
        fingerprint_code: str | None,
        password_hash: str,
    ) -> UUID: ...
