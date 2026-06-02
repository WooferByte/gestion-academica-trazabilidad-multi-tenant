import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PermissionCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    codigo: str
    descripcion: str | None = None
    modulo: str
    accion: str


class PermissionUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    descripcion: str | None = None
    modulo: str | None = None
    accion: str | None = None


class PermissionResponse(BaseModel):
    model_config = ConfigDict(extra='forbid', from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    codigo: str
    descripcion: str | None = None
    modulo: str
    accion: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class PermissionList(BaseModel):
    model_config = ConfigDict(extra='forbid')

    items: list[PermissionResponse]
    total: int
