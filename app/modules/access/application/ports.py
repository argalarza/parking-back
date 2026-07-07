from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from app.modules.access.domain.entities import AccessCandidate


class AccessRepository(Protocol):
    def update_person_face_embedding(self, person_id: UUID, embedding: list[float]) -> bool: ...

    def list_access_candidates(self) -> Sequence[AccessCandidate]: ...

    def get_gate_mqtt_topic(self, gate_id: UUID) -> str: ...


class FaceEmbeddingProvider(Protocol):
    def extract_embedding(self, image_path: str) -> list[float]: ...


class AccessControlGateway(Protocol):
    def grant_access(self, topic: str) -> None: ...

    def deny_access(self, topic: str) -> None: ...
