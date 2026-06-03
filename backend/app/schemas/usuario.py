import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UsuarioCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    email: EmailStr
    password: str
    nombre: str | None = None
    apellido: str | None = None
    dni: str | None = None
    cuil: str | None = None
    cbu: str | None = None
    alias_cbu: str | None = None
    banco: str | None = None
    regional: str | None = None
    legajo: str | None = None
    legajo_profesional: str | None = None
    facturador: bool = False
    estado: str = 'Activo'


class UsuarioUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    nombre: str | None = None
    apellido: str | None = None
    dni: str | None = None
    cuil: str | None = None
    cbu: str | None = None
    alias_cbu: str | None = None
    banco: str | None = None
    regional: str | None = None
    legajo: str | None = None
    legajo_profesional: str | None = None
    facturador: bool | None = None
    estado: str | None = None
    is_active: bool | None = None


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(extra='forbid', from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    nombre: str | None = None
    apellido: str | None = None
    legajo: str | None = None
    legajo_profesional: str | None = None
    banco: str | None = None
    regional: str | None = None
    facturador: bool
    estado: str
    is_active: bool
    roles: list[str]
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class UsuarioListResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    items: list[UsuarioResponse]
    total: int