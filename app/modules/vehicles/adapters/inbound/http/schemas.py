from pydantic import BaseModel, Field
from uuid import UUID


class VehicleCreateRequest(BaseModel):
    plate: str = Field(..., min_length=1)
    brand: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)


class VehiclePersonLinkRequest(BaseModel):
    vehicle_id: UUID
    person_id: UUID
    relation: str
