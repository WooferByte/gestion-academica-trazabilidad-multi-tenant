import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RoleCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    name: str
    codigo: str


class RoleUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    name: str | None = None
    codigo: str | None = None


class RoleResponse(BaseModel):
    model_config = ConfigDict(extra='forbid', from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    codigo: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class RoleList(BaseModel):
    model_config = ConfigDict(extra='forbid')

    items: list[RoleResponse]
    total: int
