from typing import Protocol
from uuid import UUID


class GateRepository(Protocol):
    def list_gates(self) -> list[dict]: ...

    def get_gate_by_id(self, gate_id: UUID) -> dict | None: ...

    def create_gate(
        self,
        number: int | None,
        main_street: str,
        secondary_street: str | None,
        reference: str,
    ) -> UUID: ...

    def update_gate(
        self,
        gate_id: UUID,
        number: int | None,
        main_street: str,
        secondary_street: str | None,
        reference: str,
    ) -> bool: ...

    def delete_gate(self, gate_id: UUID) -> bool: ...
