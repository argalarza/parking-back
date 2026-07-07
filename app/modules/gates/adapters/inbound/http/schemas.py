from uuid import UUID

from pydantic import BaseModel, Field


class GateCreateRequest(BaseModel):
    number: int | None = None
    main_street: str = Field(..., min_length=1)
    secondary_street: str | None = None
    reference: str = Field(..., min_length=1)


class GateUpdateRequest(BaseModel):
    number: int | None = None
    main_street: str = Field(..., min_length=1)
    secondary_street: str | None = None
    reference: str = Field(..., min_length=1)


class GateResponse(BaseModel):
    id: UUID
    number: int | None
    main_street: str
    secondary_street: str | None
    reference: str


class GateMutationResponse(BaseModel):
    success: bool
    message: str
    id: UUID | None = None
