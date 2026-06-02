import uuid

from sqlalchemy import Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class RolePermission(Base, BaseModelMixin):
    __tablename__ = 'rol_permiso'

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'), nullable=False,
    )
    permiso_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('permisos.id', ondelete='CASCADE'), nullable=False,
    )
    propio: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        UniqueConstraint('role_id', 'permiso_id', 'tenant_id', name='uq_rol_permiso'),
    )
