import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RolePermissionAssign(BaseModel):
    model_config = ConfigDict(extra='forbid')

    permiso_id: uuid.UUID
    propio: bool = False


class RolePermissionResponse(BaseModel):
    model_config = ConfigDict(extra='forbid', from_attributes=True)

    id: uuid.UUID
    role_id: uuid.UUID
    permiso_id: uuid.UUID
    propio: bool
    created_at: datetime
    deleted_at: datetime | None = None
