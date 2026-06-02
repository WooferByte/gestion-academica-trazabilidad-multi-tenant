import uuid

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Role(Base, BaseModelMixin):
    __tablename__ = 'roles'

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    codigo: Mapped[str] = mapped_column(String(50), nullable=False)

    __table_args__ = (
        UniqueConstraint('codigo', 'tenant_id', name='uq_roles_codigo_tenant'),
    )
