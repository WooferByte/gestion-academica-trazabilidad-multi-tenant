import enum
import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Index, Integer, String, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class TipoEvaluacion(str, enum.Enum):
    PARCIAL = 'Parcial'
    RECUPERATORIO = 'Recuperatorio'
    COLOQUIO = 'Coloquio'
    TP = 'TP'


class EstadoEvaluacion(str, enum.Enum):
    ACTIVA = 'Activa'
    CERRADA = 'Cerrada'


class Evaluacion(Base, BaseModelMixin):
    __tablename__ = 'evaluaciones'

    materia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('materias.id', ondelete='CASCADE'), nullable=False,
    )
    cohorte_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('cohortes.id', ondelete='CASCADE'), nullable=False,
    )
    tipo: Mapped[TipoEvaluacion] = mapped_column(
        Enum(TipoEvaluacion, name='tipo_evaluacion', values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    instancia: Mapped[str] = mapped_column(String(255), nullable=False)
    estado: Mapped[EstadoEvaluacion] = mapped_column(
        Enum(EstadoEvaluacion, name='estado_evaluacion', values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=EstadoEvaluacion.ACTIVA,
    )
    dias_disponibles: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    turnos: Mapped[list['TurnoColoquio']] = relationship(
        'TurnoColoquio', back_populates='evaluacion',
        cascade='all, delete-orphan',
    )

    __table_args__ = (
        Index('ix_evaluaciones_materia', 'materia_id', 'tenant_id'),
        Index('ix_evaluaciones_cohorte', 'cohorte_id', 'tenant_id'),
    )
