import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Cohorte(Base, BaseModelMixin):
    __tablename__ = 'cohortes'

    carrera_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('carreras.id', ondelete='CASCADE'), nullable=False,
    )
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    vig_desde: Mapped[date] = mapped_column(Date, nullable=False)
    vig_hasta: Mapped[date | None] = mapped_column(Date, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default='Activa')

    __table_args__ = (
        UniqueConstraint('tenant_id', 'carrera_id', 'nombre', name='uq_cohortes_tenant_carrera_nombre'),
    )
