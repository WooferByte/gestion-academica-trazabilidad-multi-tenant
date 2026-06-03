import enum
import uuid

from sqlalchemy import Enum, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class EstadoReserva(str, enum.Enum):
    ACTIVA = 'Activa'
    CANCELADA = 'Cancelada'


class ReservaEvaluacion(Base, BaseModelMixin):
    __tablename__ = 'reservas_evaluacion'

    turno_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('turnos_coloquio.id', ondelete='CASCADE'), nullable=False,
    )
    alumno_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False,
    )
    evaluacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('evaluaciones.id', ondelete='CASCADE'), nullable=False,
    )
    estado: Mapped[EstadoReserva] = mapped_column(
        Enum(EstadoReserva, name='estado_reserva', values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=EstadoReserva.ACTIVA,
    )

    __table_args__ = (
        UniqueConstraint('turno_id', 'alumno_id', name='uq_reserva_turno_alumno'),
        Index('ix_reservas_alumno', 'alumno_id', 'tenant_id'),
        Index('ix_reservas_evaluacion', 'evaluacion_id', 'tenant_id'),
    )
