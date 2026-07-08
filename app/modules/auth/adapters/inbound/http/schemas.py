from pydantic import BaseModel, Field


class AdminLoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class PersonLoginRequest(BaseModel):
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class AdminLoginResponse(TokenResponse):
    must_change_password: bool
    role: str


class PersonLoginResponse(TokenResponse):
    must_change_password: bool


class SuccessResponse(BaseModel):
    success: bool
    message: str
