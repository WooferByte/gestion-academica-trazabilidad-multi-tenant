import uuid
from datetime import date, time

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, Integer, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class TurnoColoquio(Base, BaseModelMixin):
    __tablename__ = 'turnos_coloquio'

    evaluacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('evaluaciones.id', ondelete='CASCADE'), nullable=False,
    )
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    hora_inicio: Mapped[time] = mapped_column(Time, nullable=False)
    hora_fin: Mapped[time] = mapped_column(Time, nullable=False)
    cupo: Mapped[int] = mapped_column(Integer, nullable=False)
    ocupados: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    evaluacion: Mapped['Evaluacion'] = relationship(
        'Evaluacion', back_populates='turnos',
    )

    __table_args__ = (
        CheckConstraint('ocupados >= 0', name='ck_turno_ocupados_positivo'),
        CheckConstraint('ocupados <= cupo', name='ck_turno_ocupados_no_excede_cupo'),
        CheckConstraint('cupo >= 0', name='ck_turno_cupo_positivo'),
        Index('ix_turnos_evaluacion', 'evaluacion_id', 'tenant_id'),
    )
