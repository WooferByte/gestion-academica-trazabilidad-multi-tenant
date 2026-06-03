import uuid

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class ResultadoEvaluacion(Base, BaseModelMixin):
    __tablename__ = 'resultados_evaluacion'

    evaluacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('evaluaciones.id', ondelete='CASCADE'), nullable=False,
    )
    alumno_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False,
    )
    nota_final: Mapped[str] = mapped_column(String(50), nullable=False)

    __table_args__ = (
        UniqueConstraint('evaluacion_id', 'alumno_id', name='uq_resultado_evaluacion_alumno'),
        Index('ix_resultados_evaluacion', 'evaluacion_id', 'tenant_id'),
    )
