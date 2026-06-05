import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class FechaAcademicaCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    tipo: str
    numero: int
    periodo: str
    fecha: date
    titulo: str


class FechaAcademicaUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    tipo: str | None = None
    numero: int | None = None
    periodo: str | None = None
    fecha: date | None = None
    titulo: str | None = None


class FechaAcademicaResponse(BaseModel):
    model_config = ConfigDict(extra='forbid', from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    tipo: str
    numero: int
    periodo: str
    fecha: date
    titulo: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class FechaAcademicaList(BaseModel):
    model_config = ConfigDict(extra='forbid')

    items: list[FechaAcademicaResponse]
    total: int
