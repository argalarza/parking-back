from pathlib import Path
from uuid import uuid4
from uuid import UUID

import numpy as np

from app.application.errors import NotFoundError, ValidationError
from app.modules.access.application.ports import (
    AccessControlGateway,
    AccessRepository,
    FaceEmbeddingProvider,
)
from app.modules.access.domain.entities import AccessResult


class EnrollFaceUseCase:
    def __init__(
        self,
        repository: AccessRepository,
        face_provider: FaceEmbeddingProvider,
        temp_dir: Path,
    ) -> None:
        self._repository = repository
        self._face_provider = face_provider
        self._temp_dir = temp_dir

    def execute(self, person_id: UUID, filename: str | None, file_bytes: bytes) -> dict:
        temp_path = self._build_temp_path(person_id=str(person_id), filename=filename)

        try:
            temp_path.write_bytes(file_bytes)
            embedding = self._face_provider.extract_embedding(str(temp_path))
            updated = self._repository.update_person_face_embedding(person_id, embedding)
            if not updated:
                raise NotFoundError("Persona no encontrada.")
            return {"success": True, "person_id": person_id}
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def _build_temp_path(self, person_id: str, filename: str | None) -> Path:
        self._temp_dir.mkdir(parents=True, exist_ok=True)
        extension = Path(filename or "rostro.jpg").suffix or ".jpg"
        return self._temp_dir / f"{person_id}_{uuid4().hex}{extension}"


class VerifyAccessUseCase:
    def __init__(
        self,
        repository: AccessRepository,
        face_provider: FaceEmbeddingProvider,
        access_control: AccessControlGateway,
        temp_dir: Path,
        match_threshold: float = 0.40,
    ) -> None:
        self._repository = repository
        self._face_provider = face_provider
        self._access_control = access_control
        self._temp_dir = temp_dir
        self._match_threshold = match_threshold

    def execute(self, gate_id: UUID, filename: str | None, file_bytes: bytes) -> AccessResult:
        temp_path = self._build_temp_path(filename=filename)

        try:
            temp_path.write_bytes(file_bytes)
            input_embedding = self._face_provider.extract_embedding(str(temp_path))
            best_match = None
            best_distance = None

            for candidate in self._repository.list_access_candidates():
                if len(candidate.embedding_face) != len(input_embedding):
                    continue

                distance = self._cosine_distance(input_embedding, candidate.embedding_face)
                if distance < self._match_threshold and (best_distance is None or distance < best_distance):
                    best_distance = distance
                    best_match = candidate

            if best_match is None:
                mqtt_topic = self._repository.get_gate_mqtt_topic(gate_id)
                self._access_control.deny_access(mqtt_topic)
                return AccessResult(
                    access=False,
                    message="Rostro no reconocido o sin vehiculo asociado",
                )

            mqtt_topic = self._repository.get_gate_mqtt_topic(gate_id)
            self._access_control.grant_access(mqtt_topic)
            return AccessResult(
                access=True,
                message="Acceso autorizado.",
                person=f"{best_match.name} {best_match.last_names}".strip(),
                vehicle=f"{best_match.plate} - {best_match.brand}",
                distance=best_distance,
            )
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def _build_temp_path(self, filename: str | None) -> Path:
        self._temp_dir.mkdir(parents=True, exist_ok=True)
        extension = Path(filename or "rostro.jpg").suffix or ".jpg"
        return self._temp_dir / f"verify_{uuid4().hex}{extension}"

    @staticmethod
    def _cosine_distance(vector_a: list[float], vector_b: list[float]) -> float:
        a = np.array(vector_a, dtype=float)
        b = np.array(vector_b, dtype=float)
        denominator = np.linalg.norm(a) * np.linalg.norm(b)
        if denominator == 0:
            raise ValidationError("No se pudo calcular la distancia coseno para el embedding facial.")
        return float(1 - np.dot(a, b) / denominator)
