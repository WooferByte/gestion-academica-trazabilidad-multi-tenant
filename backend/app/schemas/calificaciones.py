import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


VALIDOS_TEXTUALES_APROBATORIOS = frozenset({'Satisfactorio', 'Supera lo esperado'})


class ActividadDetectada(BaseModel):
    model_config = ConfigDict(extra='forbid')

    nombre: str
    tipo: str
    ejemplos: list[str] = Field(default_factory=list)


class CalificacionImportPreviewRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    materia_id: uuid.UUID
    cohorte_id: uuid.UUID


class CalificacionPreviewResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    total_filas: int
    actividades: list[ActividadDetectada]
    alumnos_ejemplo: list[dict] = Field(default_factory=list)


class ActividadAImportar(BaseModel):
    model_config = ConfigDict(extra='forbid')

    nombre: str
    tipo: str


class CalificacionConfirmRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    actividades: list[ActividadAImportar] = Field(min_length=1)


class CalificacionConfirmResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    calificaciones_creadas: int
    actividades_procesadas: list[str]


class CalificacionResponse(BaseModel):
    model_config = ConfigDict(extra='forbid', from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    entrada_padron_id: uuid.UUID
    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    actividad: str
    nota_numerica: float | None = None
    nota_textual: str | None = None
    origen: str
    importado_at: datetime
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    aprobado: bool | None = None


class CalificacionListResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    items: list[CalificacionResponse]
    total: int


class EntregaSinCorregir(BaseModel):
    model_config = ConfigDict(extra='forbid')

    alumno_nombre: str
    alumno_apellidos: str
    actividad: str
    comision: str


class ReporteFinalizacionPreviewResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    entregas_sin_corregir: list[EntregaSinCorregir]
    total: int
