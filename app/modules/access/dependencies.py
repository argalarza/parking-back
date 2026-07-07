from pathlib import Path

from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.modules.access.adapters.outbound.biometrics.deepface_provider import (
    DeepFaceEmbeddingProvider,
)
from app.modules.access.adapters.outbound.messaging.mqtt_access_control import (
    MqttAccessControlGateway,
)
from app.modules.access.adapters.outbound.persistence.postgres_repository import (
    SqlAlchemyAccessRepository,
)
from app.modules.access.application.use_cases import EnrollFaceUseCase, VerifyAccessUseCase


def get_enroll_face_use_case(db: Session = Depends(get_db)) -> EnrollFaceUseCase:
    return EnrollFaceUseCase(
        repository=SqlAlchemyAccessRepository(db),
        face_provider=DeepFaceEmbeddingProvider(),
        temp_dir=Path("app/temp"),
    )


def get_verify_access_use_case(db: Session = Depends(get_db)) -> VerifyAccessUseCase:
    return VerifyAccessUseCase(
        repository=SqlAlchemyAccessRepository(db),
        face_provider=DeepFaceEmbeddingProvider(),
        access_control=MqttAccessControlGateway(
            broker="broker.hivemq.com",
            port=1883,
        ),
        temp_dir=Path("app/temp"),
    )
