from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Permission(Base, BaseModelMixin):
    __tablename__ = 'permisos'

    codigo: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    modulo: Mapped[str] = mapped_column(String(50), nullable=False)
    accion: Mapped[str] = mapped_column(String(50), nullable=False)

    __table_args__ = (
        UniqueConstraint('codigo', 'tenant_id', name='uq_permisos_codigo_tenant'),
    )
