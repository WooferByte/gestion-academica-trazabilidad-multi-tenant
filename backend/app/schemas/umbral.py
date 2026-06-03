import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UmbralMateriaCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    asignacion_id: uuid.UUID
    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    umbral_pct: int = Field(default=60, ge=0, le=100)
    valores_aprobatorios: list[str] | None = None


class UmbralMateriaUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    umbral_pct: int = Field(default=60, ge=0, le=100)
    valores_aprobatorios: list[str] | None = None


class UmbralMateriaResponse(BaseModel):
    model_config = ConfigDict(extra='forbid', from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    asignacion_id: uuid.UUID
    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    umbral_pct: int
    valores_aprobatorios: list[str] | None = None
    created_at: datetime
    updated_at: datetime
