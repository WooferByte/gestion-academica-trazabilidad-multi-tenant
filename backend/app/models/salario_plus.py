import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class SalarioPlus(Base, BaseModelMixin):
    __tablename__ = 'salarios_plus'

    grupo: Mapped[str] = mapped_column(String(20), nullable=False)
    rol: Mapped[str] = mapped_column(String(50), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    monto: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    desde: Mapped[date] = mapped_column(Date, nullable=False)
    hasta: Mapped[date | None] = mapped_column(Date, nullable=True)

    __table_args__ = (
        Index('ix_salarios_plus_grupo_rol_vigencia', 'grupo', 'rol', 'desde', 'hasta'),
    )
