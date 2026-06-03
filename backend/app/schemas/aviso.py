import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AvisoCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    alcance: str
    materia_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    rol_destino: str | None = None
    severidad: str = 'Info'
    titulo: str = Field(..., min_length=1, max_length=500)
    cuerpo: str = Field(..., min_length=1)
    inicio_vigencia: datetime
    fin_vigencia: datetime
    orden: int = 0
    requiere_ack: bool = False


class AvisoUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    alcance: str | None = None
    materia_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    rol_destino: str | None = None
    severidad: str | None = None
    titulo: str | None = Field(None, min_length=1, max_length=500)
    cuerpo: str | None = Field(None, min_length=1)
    inicio_vigencia: datetime | None = None
    fin_vigencia: datetime | None = None
    orden: int | None = None
    activo: bool | None = None
    requiere_ack: bool | None = None


class AvisoResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    id: uuid.UUID
    tenant_id: uuid.UUID
    alcance: str
    materia_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    rol_destino: str | None = None
    severidad: str
    titulo: str
    cuerpo: str
    inicio_vigencia: datetime
    fin_vigencia: datetime
    orden: int
    activo: bool
    requiere_ack: bool
    total_acks: int = 0
    user_acked: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AvisoListResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    items: list[AvisoResponse]
    total: int


class AckResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    id: uuid.UUID
    aviso_id: uuid.UUID
    usuario_id: uuid.UUID
    confirmado_at: datetime
