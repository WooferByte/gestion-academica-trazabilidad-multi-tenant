from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Carrera(Base, BaseModelMixin):
    __tablename__ = 'carreras'

    codigo: Mapped[str] = mapped_column(String(50), nullable=False)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default='Activa')

    __table_args__ = (
        UniqueConstraint('codigo', 'tenant_id', name='uq_carreras_codigo_tenant'),
    )
