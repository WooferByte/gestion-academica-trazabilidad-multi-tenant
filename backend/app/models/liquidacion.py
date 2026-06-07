import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Liquidacion(Base, BaseModelMixin):
    __tablename__ = 'liquidaciones'

    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False,
    )
    cohorte_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('cohortes.id', ondelete='CASCADE'), nullable=False,
    )
    periodo: Mapped[str] = mapped_column(String(7), nullable=False)
    rol: Mapped[str] = mapped_column(String(50), nullable=False)
    monto_base: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    monto_plus: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    es_nexo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    excluido_por_factura: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default='Abierta')

    __table_args__ = (
        Index('ix_liquidaciones_cohorte_periodo', 'cohorte_id', 'periodo'),
        Index('ix_liquidaciones_usuario', 'usuario_id'),
        Index('ix_liquidaciones_estado', 'estado'),
    )
