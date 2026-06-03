import uuid
from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field


class TurnoColoquioCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    fecha: date
    hora_inicio: str = Field(..., pattern=r'^\d{2}:\d{2}$')
    hora_fin: str = Field(..., pattern=r'^\d{2}:\d{2}$')
    cupo: int = Field(..., ge=1)


class TurnoColoquioResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    id: uuid.UUID
    evaluacion_id: uuid.UUID
    fecha: date
    hora_inicio: time
    hora_fin: time
    cupo: int
    ocupados: int
    created_at: datetime | None = None
    updated_at: datetime | None = None


class EvaluacionCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    instancia: str = Field(..., min_length=1, max_length=255)
    tipo: str
    turnos: list[TurnoColoquioCreate] = Field(..., min_length=1)


class EvaluacionResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    id: uuid.UUID
    tenant_id: uuid.UUID
    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    tipo: str
    instancia: str
    estado: str
    dias_disponibles: int
    turnos: list[TurnoColoquioResponse] = []
    total_convocados: int = 0
    reservas_activas: int = 0
    cupos_libres: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None


class EvaluacionListResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    items: list[EvaluacionResponse]
    total: int


class ReservaCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    turno_id: uuid.UUID


class ReservaResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    id: uuid.UUID
    turno_id: uuid.UUID
    alumno_id: uuid.UUID
    evaluacion_id: uuid.UUID
    estado: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ReservaCancelResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    id: uuid.UUID
    estado: str
    mensaje: str = 'Reserva cancelada exitosamente'


class ResultadoCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    nota_final: str = Field(..., min_length=1, max_length=50)


class ResultadoUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    nota_final: str = Field(..., min_length=1, max_length=50)


class ResultadoResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    id: uuid.UUID
    evaluacion_id: uuid.UUID
    alumno_id: uuid.UUID
    nota_final: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ResultadosListResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    items: list[ResultadoResponse]
    total: int


class MetricasColoquiosResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    total_convocatorias_activas: int
    total_alumnos_convocados: int
    total_reservas_activas: int
    total_resultados_registrados: int


class AlumnosImportRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    alumno_ids: list[uuid.UUID]
