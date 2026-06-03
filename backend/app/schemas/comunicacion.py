import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ComunicacionPreviewRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    destinatario: str = Field(..., min_length=1)
    asunto: str = Field(..., min_length=1)
    cuerpo: str = Field(..., min_length=1)
    variables: dict[str, str] = Field(default_factory=dict)


class ComunicacionPreviewResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    asunto_renderizado: str
    cuerpo_renderizado: str
    variables_no_encontradas: list[str] = Field(default_factory=list)


class ComunicacionCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    materia_id: uuid.UUID | None = None
    destinatario: str = Field(..., min_length=1)
    asunto: str = Field(..., min_length=1)
    cuerpo: str = Field(..., min_length=1)
    programada_para: datetime | None = None


class ComunicacionBulkCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    materia_id: uuid.UUID | None = None
    destinatarios: list[str] = Field(..., min_length=1)
    asunto: str = Field(..., min_length=1)
    cuerpo: str = Field(..., min_length=1)
    programada_para: datetime | None = None


class ComunicacionResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    id: uuid.UUID
    tenant_id: uuid.UUID
    enviado_por: uuid.UUID | None = None
    materia_id: uuid.UUID | None = None
    destinatario: str
    asunto: str
    cuerpo: str
    estado: str
    lote_id: uuid.UUID
    aprobacion_requerida: bool
    error_msg: str | None = None
    programada_para: datetime | None = None
    enviada_at: datetime | None = None
    aprobada_por: uuid.UUID | None = None
    cancelada_por: uuid.UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ComunicacionListResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    items: list[ComunicacionResponse]
    total: int


class AprobarLoteRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    lote_id: uuid.UUID
    accion: str = Field(..., pattern='^(aprobar|rechazar)$')


class CancelarRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    comunicacion_id: uuid.UUID
