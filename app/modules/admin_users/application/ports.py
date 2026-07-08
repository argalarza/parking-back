from typing import Protocol
from uuid import UUID


class AdminUserRepository(Protocol):
    def list_admin_users(self) -> list[dict]: ...

    def get_admin_user_by_id(self, user_id: UUID) -> dict | None: ...

    def create_admin_user(
        self,
        username: str,
        full_name: str,
        email: str,
        role: str,
        password_hash: str,
    ) -> UUID: ...

    def set_admin_active(self, user_id: UUID, is_active: bool) -> bool: ...
