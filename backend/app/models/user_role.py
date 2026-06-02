import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class UserRole(Base, BaseModelMixin):
    __tablename__ = 'user_roles'

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False,
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'), nullable=False,
    )
    desde: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    hasta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', 'tenant_id', name='uq_user_roles'),
    )
