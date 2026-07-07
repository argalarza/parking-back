from app.modules.auth.application.use_cases import pwd_context
from app.modules.guests.application.ports import GuestRepository


class RegisterGuestUseCase:
    def __init__(self, repository: GuestRepository) -> None:
        self._repository = repository

    def execute(
        self,
        first_names: str,
        last_names: str,
        dni_type: str,
        dni: str,
        phone: str,
        email: str,
        fingerprint_code: str | None,
        password: str,
    ) -> dict:
        password_hash = pwd_context.hash(password)
        person_id = self._repository.register_guest(
            dni=dni,
            dni_type=dni_type,
            first_names=first_names,
            last_names=last_names,
            phone=phone,
            email=email,
            fingerprint_code=fingerprint_code,
            password_hash=password_hash,
        )
        return {
            "success": True,
            "person_id": person_id,
        }
