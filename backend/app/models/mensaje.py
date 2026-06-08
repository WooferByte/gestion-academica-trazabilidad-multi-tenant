import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class MensajeHilo(Base, BaseModelMixin):
    __tablename__ = 'mensajes_hilo'

    participant_user_ids: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    last_message_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    messages: Mapped[list['Mensaje']] = relationship(
        back_populates='hilo', cascade='all, delete-orphan',
    )

    __table_args__ = (
        Index('ix_mensajes_hilo_participants', 'participant_user_ids', postgresql_using='gin'),
    )


class Mensaje(Base, BaseModelMixin):
    __tablename__ = 'mensajes'

    hilo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('mensajes_hilo.id', ondelete='CASCADE'), nullable=False,
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False,
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    hilo: Mapped['MensajeHilo'] = relationship(back_populates='messages')
    sender: Mapped['User'] = relationship(back_populates='mensajes_enviados')

    __table_args__ = (
        Index('ix_mensajes_hilo_id', 'hilo_id'),
        Index('ix_mensajes_sender_id', 'sender_id'),
    )
