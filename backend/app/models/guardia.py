import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin
from app.models.slot_encuentro import DiaSemana


class EstadoGuardia(str, enum.Enum):
    PENDIENTE = 'Pendiente'
    REALIZADA = 'Realizada'
    CANCELADA = 'Cancelada'


class Guardia(Base, BaseModelMixin):
    __tablename__ = 'guardias'

    asignacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('asignaciones.id', ondelete='CASCADE'), nullable=False,
    )
    materia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('materias.id', ondelete='CASCADE'), nullable=False,
    )
    carrera_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('carreras.id', ondelete='SET NULL'), nullable=True,
    )
    cohorte_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('cohortes.id', ondelete='SET NULL'), nullable=True,
    )
    dia: Mapped[DiaSemana] = mapped_column(
        Enum(DiaSemana, name='dia_semana', values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    horario: Mapped[str] = mapped_column(String(20), nullable=False)
    estado: Mapped[EstadoGuardia] = mapped_column(
        Enum(EstadoGuardia, name='estado_guardia', values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=EstadoGuardia.PENDIENTE,
    )
    comentarios: Mapped[str | None] = mapped_column(Text, nullable=True)
    creada_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )

    __table_args__ = (
        Index('ix_guardias_materia', 'materia_id', 'tenant_id'),
        Index('ix_guardias_asignacion', 'asignacion_id', 'tenant_id'),
    )
