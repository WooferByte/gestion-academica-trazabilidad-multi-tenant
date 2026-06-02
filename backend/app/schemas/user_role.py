import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserRoleAssign(BaseModel):
    model_config = ConfigDict(extra='forbid')

    role_id: uuid.UUID


class UserRoleResponse(BaseModel):
    model_config = ConfigDict(extra='forbid', from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    role_id: uuid.UUID
    desde: datetime | None = None
    hasta: datetime | None = None
    created_at: datetime
    deleted_at: datetime | None = None
