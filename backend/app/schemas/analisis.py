import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AlumnoAtrasado(BaseModel):
    model_config = ConfigDict(extra='forbid')

    entrada_padron_id: uuid.UUID
    nombre: str
    apellidos: str
    email: str
    comision: str
    regional: str
    actividades_faltantes: list[str]
    actividades_desaprobadas: list[str]
    total_actividades: int
    aprobadas: int


class RankingEntry(BaseModel):
    model_config = ConfigDict(extra='forbid')

    entrada_padron_id: uuid.UUID
    nombre: str
    apellidos: str
    comision: str
    actividades_aprobadas: int


class ReporteRapido(BaseModel):
    model_config = ConfigDict(extra='forbid')

    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    total_alumnos: int
    total_actividades: int
    alumnos_aprobados: int
    alumnos_atrasados: int
    promedio_general: float | None = None


class NotaFinal(BaseModel):
    model_config = ConfigDict(extra='forbid')

    entrada_padron_id: uuid.UUID
    nombre: str
    apellidos: str
    nota_final: float | None = None
    actividades_consideradas: int


class TPSinCorregir(BaseModel):
    model_config = ConfigDict(extra='forbid')

    alumno_nombre: str
    alumno_apellidos: str
    actividad: str
    comision: str


class MonitorEntry(BaseModel):
    model_config = ConfigDict(extra='forbid')

    entrada_padron_id: uuid.UUID
    nombre: str
    apellidos: str
    comision: str
    regional: str
    materia_id: uuid.UUID
    materia_nombre: str
    actividad: str
    nota_numerica: float | None = None
    nota_textual: str | None = None
    aprobado: bool | None = None
    importado_at: datetime | None = None


class MonitorSeguimiento(BaseModel):
    model_config = ConfigDict(extra='forbid')

    entrada_padron_id: uuid.UUID
    nombre: str
    apellidos: str
    comision: str
    materia_id: uuid.UUID
    actividad: str
    nota_numerica: float | None = None
    nota_textual: str | None = None
    aprobado: bool | None = None
    importado_at: datetime | None = None
