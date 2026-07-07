from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AccessCandidate:
    person_id: UUID
    name: str
    last_names: str
    embedding_face: list[float]
    plate: str
    brand: str


@dataclass(frozen=True)
class AccessResult:
    access: bool
    message: str
    person: str | None = None
    vehicle: str | None = None
    distance: float | None = None
