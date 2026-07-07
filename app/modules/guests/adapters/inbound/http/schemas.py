from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class GuestRegisterRequest(BaseModel):
    first_names: str = Field(..., min_length=1)
    last_names: str = Field(..., min_length=1)
    dni_type: Literal["CEDULA", "PASAPORTE"]
    dni: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=1)
    email: EmailStr
    fingerprint_code: str | None = None
    password: str = Field(..., min_length=8)


class GuestRegisterResponse(BaseModel):
    success: bool
    person_id: UUID
