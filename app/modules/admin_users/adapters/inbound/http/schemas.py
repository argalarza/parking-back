from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


AdminRole = Literal["admin", "admin_ti", "asesor", "operador", "supervisor"]


class AdminUserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=150)
    email: EmailStr
    role: AdminRole


class AdminUserStatusRequest(BaseModel):
    is_active: bool


class AdminUserResponse(BaseModel):
    id: UUID
    username: str
    full_name: str | None
    email: str | None
    role: str
    is_active: bool
    must_change_password: bool
    created_date: datetime
    last_modified_date: datetime


class AdminUserCreateResponse(BaseModel):
    success: bool
    message: str
    id: UUID
    email_sent: bool
    email_message: str


class AdminUserMutationResponse(BaseModel):
    success: bool
    message: str
