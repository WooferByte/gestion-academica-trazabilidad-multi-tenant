import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PerfilResponse(BaseModel):
    model_config = ConfigDict(extra='forbid', from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
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
    facturador: bool
    estado: str
    roles: list[str]
    created_at: datetime
    updated_at: datetime


class PerfilUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    nombre: str | None = None
    apellido: str | None = None
    cbu: str | None = None
    alias_cbu: str | None = None
    banco: str | None = None
    regional: str | None = None
    facturador: bool | None = None
