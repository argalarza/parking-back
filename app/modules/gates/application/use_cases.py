from uuid import UUID

from app.application.errors import NotFoundError
from app.modules.gates.application.ports import GateRepository


class ListGatesUseCase:
    def __init__(self, repository: GateRepository) -> None:
        self._repository = repository

    def execute(self) -> list[dict]:
        return self._repository.list_gates()


class GetGateUseCase:
    def __init__(self, repository: GateRepository) -> None:
        self._repository = repository

    def execute(self, gate_id: UUID) -> dict:
        gate = self._repository.get_gate_by_id(gate_id)
        if gate is None:
            raise NotFoundError("Puerta no encontrada.")
        return gate


class CreateGateUseCase:
    def __init__(self, repository: GateRepository) -> None:
        self._repository = repository

    def execute(
        self,
        number: int | None,
        main_street: str,
        secondary_street: str | None,
        reference: str,
    ) -> dict:
        gate_id = self._repository.create_gate(
            number=number,
            main_street=main_street,
            secondary_street=secondary_street,
            reference=reference,
        )
        return {
            "success": True,
            "message": "Puerta creada correctamente.",
            "id": gate_id,
        }


class UpdateGateUseCase:
    def __init__(self, repository: GateRepository) -> None:
        self._repository = repository

    def execute(
        self,
        gate_id: UUID,
        number: int | None,
        main_street: str,
        secondary_street: str | None,
        reference: str,
    ) -> dict:
        updated = self._repository.update_gate(
            gate_id=gate_id,
            number=number,
            main_street=main_street,
            secondary_street=secondary_street,
            reference=reference,
        )
        if not updated:
            raise NotFoundError("Puerta no encontrada.")
        return {
            "success": True,
            "message": "Puerta actualizada correctamente.",
        }


class DeleteGateUseCase:
    def __init__(self, repository: GateRepository) -> None:
        self._repository = repository

    def execute(self, gate_id: UUID) -> dict:
        deleted = self._repository.delete_gate(gate_id)
        if not deleted:
            raise NotFoundError("Puerta no encontrada.")
        return {
            "success": True,
            "message": "Puerta eliminada correctamente.",
        }
