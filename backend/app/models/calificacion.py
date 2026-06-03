import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Calificacion(Base, BaseModelMixin):
    __tablename__ = 'calificaciones'

    entrada_padron_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('entrada_padron.id', ondelete='CASCADE'), nullable=False,
    )
    materia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('materias.id', ondelete='CASCADE'), nullable=False,
    )
    cohorte_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('cohortes.id', ondelete='CASCADE'), nullable=False,
    )
    actividad: Mapped[str] = mapped_column(String(255), nullable=False)
    nota_numerica: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    nota_textual: Mapped[str | None] = mapped_column(String(255), nullable=True)
    origen: Mapped[str] = mapped_column(String(20), nullable=False, default='Importado')
    importado_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )

    __table_args__ = (
        Index('ix_calificaciones_materia_cohorte', 'materia_id', 'cohorte_id'),
        Index('ix_calificaciones_entrada_padron', 'entrada_padron_id'),
    )
