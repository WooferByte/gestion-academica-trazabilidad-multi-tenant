import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AccionPorDiaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')

    fecha: date
    accion: str
    total: int


class ComunicacionesDocenteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')

    usuario_id: uuid.UUID
    docente_email: str | None = None
    pendientes: int = 0
    enviadas: int = 0
    fallidas: int = 0


class InteraccionesDocenteMateriaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')

    usuario_id: uuid.UUID
    materia_id: uuid.UUID | None = None
    accion: str
    total: int


class LogEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')

    id: uuid.UUID
    fecha_hora: datetime
    actor_id: uuid.UUID
    impersonado_id: uuid.UUID | None = None
    materia_id: uuid.UUID | None = None
    accion: str
    detalle: dict | None = None
    filas_afectadas: int
    ip: str
    user_agent: str


class AuditoriaLogQuery(BaseModel):
    model_config = ConfigDict(extra='forbid')

    fecha_desde: date | None = None
    fecha_hasta: date | None = None
    materia_id: uuid.UUID | None = None
    usuario_id: uuid.UUID | None = None
    accion: str | None = None
    max_records: int = Field(default=200, ge=1)

    @field_validator('max_records')
    @classmethod
    def validate_max_records(cls, v: int) -> int:
        if v > 1000:
            return 1000
        if v < 1:
            return 1
        return v


class AccionesPorDiaQuery(BaseModel):
    model_config = ConfigDict(extra='forbid')

    fecha_desde: date | None = None
    fecha_hasta: date | None = None


class ComunicacionesQuery(BaseModel):
    model_config = ConfigDict(extra='forbid')

    fecha_desde: date | None = None
    fecha_hasta: date | None = None
    materia_id: uuid.UUID | None = None
    usuario_id: uuid.UUID | None = None


class InteraccionesQuery(BaseModel):
    model_config = ConfigDict(extra='forbid')

    fecha_desde: date | None = None
    fecha_hasta: date | None = None
    materia_id: uuid.UUID | None = None
    usuario_id: uuid.UUID | None = None
