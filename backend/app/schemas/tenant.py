import uuid
from datetime import datetime

from pydantic import ConfigDict
from pydantic import BaseModel


class TenantCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    nombre: str
    codigo: str


class TenantUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    nombre: str | None = None
    codigo: str | None = None
    estado: str | None = None


class TenantOut(BaseModel):
    model_config = ConfigDict(extra='forbid', from_attributes=True)
    id: uuid.UUID
    nombre: str
    codigo: str
    estado: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
