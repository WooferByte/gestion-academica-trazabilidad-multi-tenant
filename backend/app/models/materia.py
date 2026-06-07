import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Materia(Base, BaseModelMixin):
    __tablename__ = 'materias'

    codigo: Mapped[str] = mapped_column(String(50), nullable=False)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    categoria_plus_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey('categorias_plus.id'), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default='Activa')

    __table_args__ = (
        UniqueConstraint('codigo', 'tenant_id', name='uq_materias_codigo_tenant'),
    )
