import enum
import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Index, String, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class DiaSemana(str, enum.Enum):
    LUNES = 'Lunes'
    MARTES = 'Martes'
    MIERCOLES = 'Miercoles'
    JUEVES = 'Jueves'
    VIERNES = 'Viernes'
    SABADO = 'Sabado'
    DOMINGO = 'Domingo'


class SlotEncuentro(Base, BaseModelMixin):
    __tablename__ = 'slots_encuentro'

    asignacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('asignaciones.id', ondelete='CASCADE'), nullable=False,
    )
    materia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('materias.id', ondelete='CASCADE'), nullable=False,
    )
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    hora: Mapped[str] = mapped_column(String(5), nullable=False)
    dia_semana: Mapped[DiaSemana] = mapped_column(
        Enum(DiaSemana, name='dia_semana', values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    cant_semanas: Mapped[int] = mapped_column(nullable=False, default=0)
    fecha_unica: Mapped[date | None] = mapped_column(Date, nullable=True)
    meet_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    vig_desde: Mapped[date | None] = mapped_column(Date, nullable=True)
    vig_hasta: Mapped[date | None] = mapped_column(Date, nullable=True)

    __table_args__ = (
        Index('ix_slots_encuentro_materia', 'materia_id', 'tenant_id'),
    )
