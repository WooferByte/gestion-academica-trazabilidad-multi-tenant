import uuid

from sqlalchemy import ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class UmbralMateria(Base, BaseModelMixin):
    __tablename__ = 'umbral_materia'

    asignacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('asignaciones.id', ondelete='CASCADE'), nullable=False,
    )
    materia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('materias.id', ondelete='CASCADE'), nullable=False,
    )
    cohorte_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('cohortes.id', ondelete='CASCADE'), nullable=False,
    )
    umbral_pct: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    valores_aprobatorios: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        Index('ix_umbral_materia_materia_cohorte', 'materia_id', 'cohorte_id'),
    )
