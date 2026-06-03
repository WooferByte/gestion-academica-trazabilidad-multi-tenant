import enum
import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Index, String, Text, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class EstadoInstancia(str, enum.Enum):
    PROGRAMADO = 'Programado'
    REALIZADO = 'Realizado'
    CANCELADO = 'Cancelado'


class InstanciaEncuentro(Base, BaseModelMixin):
    __tablename__ = 'instancias_encuentro'

    slot_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('slots_encuentro.id', ondelete='SET NULL'), nullable=True,
    )
    materia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('materias.id', ondelete='CASCADE'), nullable=False,
    )
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    hora: Mapped[str] = mapped_column(String(5), nullable=False)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    estado: Mapped[EstadoInstancia] = mapped_column(
        Enum(EstadoInstancia, name='estado_instancia', values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=EstadoInstancia.PROGRAMADO,
    )
    meet_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    comentario: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index('ix_instancias_materia_fecha', 'materia_id', 'fecha', 'tenant_id'),
        Index('ix_instancias_slot_id', 'slot_id'),
    )
