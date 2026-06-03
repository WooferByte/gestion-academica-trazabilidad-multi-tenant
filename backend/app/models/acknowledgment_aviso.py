import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class AcknowledgmentAviso(Base, BaseModelMixin):
    __tablename__ = 'acknowledgment_avisos'

    aviso_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('avisos.id', ondelete='CASCADE'), nullable=False,
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False,
    )
    confirmado_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )

    __table_args__ = (
        UniqueConstraint('aviso_id', 'usuario_id', name='uq_ack_aviso_usuario'),
        Index('ix_ack_aviso', 'aviso_id'),
        Index('ix_ack_usuario', 'usuario_id'),
    )
