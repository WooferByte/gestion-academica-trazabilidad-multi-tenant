import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MensajeResponse(BaseModel):
    model_config = ConfigDict(extra='forbid', from_attributes=True)

    id: uuid.UUID
    hilo_id: uuid.UUID
    sender_id: uuid.UUID
    sender_nombre: str | None = None
    body: str
    read_at: datetime | None = None
    created_at: datetime


class HiloResponse(BaseModel):
    model_config = ConfigDict(extra='forbid', from_attributes=True)

    id: uuid.UUID
    subject: str
    participant_ids: list[uuid.UUID]
    last_message_preview: str | None = None
    last_message_at: datetime | None = None
    unread_count: int = 0
    created_at: datetime
    updated_at: datetime


class HiloListResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    items: list[HiloResponse]
    total: int


class ReplyRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    body: str = Field(min_length=1)


class NuevoMensajeRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    recipient_id: uuid.UUID
    subject: str = Field(min_length=1, max_length=500)
    body: str = Field(min_length=1)
