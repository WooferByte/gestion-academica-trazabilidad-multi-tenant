import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Asignacion(Base, BaseModelMixin):
    __tablename__ = 'asignaciones'

    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False,
    )
    rol: Mapped[str] = mapped_column(String(50), nullable=False)
    materia_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('materias.id', ondelete='SET NULL'), nullable=True,
    )
    carrera_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('carreras.id', ondelete='SET NULL'), nullable=True,
    )
    cohorte_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('cohortes.id', ondelete='SET NULL'), nullable=True,
    )
    comisiones: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    responsable_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True,
    )
    desde: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    hasta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index('ix_asignaciones_usuario_id', 'usuario_id'),
        Index('ix_asignaciones_rol', 'rol'),
        Index('ix_asignaciones_materia_id', 'materia_id'),
        Index('ix_asignaciones_responsable_id', 'responsable_id'),
    )