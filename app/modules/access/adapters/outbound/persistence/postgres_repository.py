from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import Float, bindparam, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.application.errors import RepositoryError, ValidationError
from app.modules.access.domain.entities import AccessCandidate


class SqlAlchemyAccessRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def update_person_face_embedding(self, person_id: UUID, embedding: list[float]) -> bool:
        try:
            query = text(
                """
                UPDATE uce.core_persons
                SET embedding_face = :embedding
                WHERE id = :person_id
                """
            ).bindparams(bindparam("embedding", type_=ARRAY(Float)))
            result = self._db.execute(query, {"embedding": embedding, "person_id": str(person_id)})
            if result.rowcount == 0:
                self._db.rollback()
                return False
            self._db.commit()
            return True
        except SQLAlchemyError as exc:
            self._db.rollback()
            raise RepositoryError("Error al actualizar el embedding facial.") from exc

    def list_access_candidates(self) -> Sequence[AccessCandidate]:
        try:
            result = self._db.execute(
                text(
                    """
                    SELECT
                        p.id,
                        p.name,
                        p.last_names,
                        p.embedding_face,
                        v.plate,
                        v.brand
                    FROM uce.core_persons p
                    JOIN uce.vehicle_persons vp ON vp.person_id = p.id
                    JOIN uce.core_vehicles v ON v.id = vp.vehicle_id
                    WHERE p.embedding_face IS NOT NULL
                    """
                )
            )
            rows = result.mappings().all()
            return [
                AccessCandidate(
                    person_id=row["id"],
                    name=row["name"],
                    last_names=row["last_names"],
                    embedding_face=list(row["embedding_face"] or []),
                    plate=row["plate"],
                    brand=row["brand"],
                )
                for row in rows
                if row["embedding_face"]
            ]
        except SQLAlchemyError as exc:
            raise RepositoryError("Error al consultar los embeddings faciales.") from exc

    def get_gate_mqtt_topic(self, gate_id: UUID) -> str:
        try:
            result = self._db.execute(
                text(
                    """
                    SELECT mqtt_topic
                    FROM uce.gates
                    WHERE id = :gate_id
                    """
                ),
                {"gate_id": gate_id},
            )
            mqtt_topic = result.scalar_one_or_none()
            if mqtt_topic is None:
                raise ValidationError("La puerta no existe o no tiene mqtt_topic configurado.")
            if not str(mqtt_topic).strip():
                raise ValidationError("La puerta no existe o no tiene mqtt_topic configurado.")
            return str(mqtt_topic)
        except ValidationError:
            raise
        except SQLAlchemyError as exc:
            raise RepositoryError("Error al consultar el topic MQTT de la puerta.") from exc
