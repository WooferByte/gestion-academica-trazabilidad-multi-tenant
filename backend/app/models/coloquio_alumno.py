import uuid

from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class ColoquioAlumno(Base, BaseModelMixin):
    __tablename__ = 'coloquio_alumnos'

    evaluacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('evaluaciones.id', ondelete='CASCADE'), nullable=False,
    )
    alumno_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False,
    )

    __table_args__ = (
        UniqueConstraint('evaluacion_id', 'alumno_id', name='uq_coloquio_alumno'),
        Index('ix_coloquio_alumnos_evaluacion', 'evaluacion_id', 'tenant_id'),
        Index('ix_coloquio_alumnos_alumno', 'alumno_id', 'tenant_id'),
    )
