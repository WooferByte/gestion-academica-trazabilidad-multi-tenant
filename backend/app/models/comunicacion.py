import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class EstadoComunicacion(str, enum.Enum):
    PENDIENTE = 'Pendiente'
    ENVIANDO = 'Enviando'
    ENVIADO = 'Enviado'
    ERROR = 'Error'
    CANCELADO = 'Cancelado'


class Comunicacion(Base, BaseModelMixin):
    __tablename__ = 'comunicaciones'

    enviado_por: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
    )
    materia_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('materias.id', ondelete='SET NULL'),
        nullable=True,
    )
    destinatario: Mapped[str] = mapped_column(Text, nullable=False)
    asunto: Mapped[str] = mapped_column(String(500), nullable=False)
    cuerpo: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[EstadoComunicacion] = mapped_column(
        Enum(EstadoComunicacion, name='estado_comunicacion'),
        nullable=False,
        default=EstadoComunicacion.PENDIENTE,
    )
    lote_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    aprobacion_requerida: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
    )
    error_msg: Mapped[str | None] = mapped_column(Text, nullable=True)
    programada_para: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    enviada_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    aprobada_por: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
    )
    cancelada_por: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
    )

    __table_args__ = (
        Index('ix_comunicaciones_estado_tenant', 'estado', 'tenant_id', 'deleted_at'),
        Index('ix_comunicaciones_lote_tenant', 'lote_id', 'tenant_id'),
    )
