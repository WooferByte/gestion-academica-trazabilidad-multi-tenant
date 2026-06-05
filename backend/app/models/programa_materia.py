import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class ProgramaMateria(Base, BaseModelMixin):
    __tablename__ = 'programas_materia'

    materia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('materias.id', ondelete='CASCADE'), nullable=False,
    )
    carrera_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('carreras.id', ondelete='CASCADE'), nullable=False,
    )
    cohorte_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('cohortes.id', ondelete='CASCADE'), nullable=False,
    )
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    referencia_archivo: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cargado_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint('materia_id', 'carrera_id', 'cohorte_id', name='uq_programas_materia_unique'),
    )
