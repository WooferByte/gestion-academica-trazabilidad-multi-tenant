import uuid
from datetime import date
from enum import Enum

from sqlalchemy import Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class TipoFechaAcademica(str, Enum):
    PARCIAL = 'Parcial'
    TP = 'TP'
    COLOQUIO = 'Coloquio'
    RECUPERATORIO = 'Recuperatorio'


class FechaAcademica(Base, BaseModelMixin):
    __tablename__ = 'fechas_academicas'

    materia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('materias.id', ondelete='CASCADE'), nullable=False,
    )
    cohorte_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('cohortes.id', ondelete='CASCADE'), nullable=False,
    )
    tipo: Mapped[TipoFechaAcademica] = mapped_column(
        String(20), nullable=False,
    )
    numero: Mapped[int] = mapped_column(Integer, nullable=False)
    periodo: Mapped[str] = mapped_column(String(20), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
