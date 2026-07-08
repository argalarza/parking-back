from typing import Annotated
from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import Form
from pydantic import BaseModel, EmailStr, Field


class SubscriberRegistrationForm(BaseModel):
    first_names: str = Field(..., min_length=1)
    last_names: str = Field(..., min_length=1)
    email: EmailStr
    phone: str = Field(..., min_length=1)
    dni: str = Field(..., min_length=1)

    @classmethod
    def as_form(
        cls,
        first_names: Annotated[str, Form(...)],
        last_names: Annotated[str, Form(...)],
        email: Annotated[EmailStr, Form(...)],
        phone: Annotated[str, Form(...)],
        dni: Annotated[str, Form(...)],
    ) -> "SubscriberRegistrationForm":
        return cls(
            first_names=first_names,
            last_names=last_names,
            email=email,
            phone=phone,
            dni=dni,
        )


class SubscriberRegistrationResponse(BaseModel):
    success: bool
    message: str
    person_id: UUID
    email_sent: bool
    email_message: str


class MySubscriptionResponse(BaseModel):
    id: UUID
    dni: str | None
    first_names: str | None
    last_names: str | None
    email: str | None
    phone: str | None
    must_change_password: bool
    amount: Decimal | None
    payment_date: date | None
    valid_from: date | None
    valid_until: date | None
    status: str | None
    is_active: bool


class SubscriberListItem(BaseModel):
    id: UUID
    dni: str | None
    first_names: str | None
    last_names: str | None
    email: str | None
    phone: str | None
    is_active: bool
    amount: Decimal | None
    payment_date: date | None
    valid_from: date | None
    valid_until: date | None
    status: str | None
    subscription_active: bool
