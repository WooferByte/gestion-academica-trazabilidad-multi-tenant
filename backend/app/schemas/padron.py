import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EntradaPadronResponse(BaseModel):
    model_config = ConfigDict(extra='forbid', from_attributes=True)

    id: uuid.UUID
    version_id: uuid.UUID
    tenant_id: uuid.UUID
    usuario_id: uuid.UUID | None = None
    nombre: str
    apellidos: str
    email: str
    comision: str
    regional: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class VersionPadronResponse(BaseModel):
    model_config = ConfigDict(extra='forbid', from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    cargado_por: uuid.UUID
    cargado_at: datetime
    activa: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class ImportPreviewItem(BaseModel):
    model_config = ConfigDict(extra='forbid')

    nombre: str
    apellidos: str
    email: str
    comision: str
    regional: str


class ImportPreviewResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    total: int
    items: list[ImportPreviewItem]


class ImportConfirmRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    items: list[ImportPreviewItem] = Field(min_length=1)


class PadronVaciarResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    materia_id: uuid.UUID
    entradas_afectadas: int
    version_desactivada: bool
