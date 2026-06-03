import uuid

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class EntradaPadron(Base, BaseModelMixin):
    __tablename__ = 'entrada_padron'

    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('version_padron.id', ondelete='CASCADE'), nullable=False,
    )
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True,
    )
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    comision: Mapped[str] = mapped_column(String(50), nullable=False)
    regional: Mapped[str] = mapped_column(String(100), nullable=False)

    __table_args__ = (
        Index('ix_entrada_padron_version_id', 'version_id'),
    )
