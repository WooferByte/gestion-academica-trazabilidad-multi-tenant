import uuid
from datetime import datetime

from sqlalchemy import Boolean, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Tenant(Base, BaseModelMixin):
    __tablename__ = 'tenants'

    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    codigo: Mapped[str] = mapped_column(String(50), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default='Activo')
    aprobacion_comunicaciones: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
    )

    __table_args__ = (
        UniqueConstraint('codigo', name='uq_tenants_codigo'),
        Index('ix_tenants_codigo', 'codigo'),
    )
