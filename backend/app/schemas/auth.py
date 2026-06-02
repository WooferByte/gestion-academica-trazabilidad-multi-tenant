import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    email: EmailStr
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
    expires_in: int


class Login2FARequired(BaseModel):
    model_config = ConfigDict(extra='forbid')

    fa2_required: bool = Field(default=True, serialization_alias='2fa_required')
    fa2_token: str = Field(serialization_alias='2fa_token')


class RefreshRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    refresh_token: str


class RefreshResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
    expires_in: int


class LogoutRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    refresh_token: str


class TOTPEnrollResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    secret: str
    uri: str


class TOTPVerifyRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    secret: str
    code: str = Field(min_length=6, max_length=6)


class TOTPValidateRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', populate_by_name=True)

    fa2_token: str = Field(alias='2fa_token')
    code: str = Field(min_length=6, max_length=6)


class ForgotRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    email: EmailStr


class ForgotResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    detail: str
    token: str | None = None
    expires_in: int | None = None


class ResetRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    token: str
    new_password: str = Field(min_length=8)


class ResetResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    detail: str


class UserContext(BaseModel):
    model_config = ConfigDict(extra='forbid')

    user_id: uuid.UUID
    tenant_id: uuid.UUID
    roles: list[str]
    impersonator_id: uuid.UUID | None = None


class UserCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    email: EmailStr
    password: str = Field(min_length=8)
    nombre: str | None = None
    apellido: str | None = None
    dni: str | None = None
    roles: list[str] = Field(default_factory=list)
    is_active: bool = True
