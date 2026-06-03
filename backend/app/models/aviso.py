import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class AlcanceAviso(str, enum.Enum):
    GLOBAL = 'Global'
    POR_MATERIA = 'PorMateria'
    POR_COHORTE = 'PorCohorte'
    POR_ROL = 'PorRol'


class SeveridadAviso(str, enum.Enum):
    INFO = 'Info'
    ADVERTENCIA = 'Advertencia'
    CRITICO = 'Crítico'


class Aviso(Base, BaseModelMixin):
    __tablename__ = 'avisos'

    alcance: Mapped[AlcanceAviso] = mapped_column(
        Enum(AlcanceAviso, name='alcance_aviso', values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    materia_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('materias.id', ondelete='SET NULL'),
        nullable=True,
    )
    cohorte_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('cohortes.id', ondelete='SET NULL'),
        nullable=True,
    )
    rol_destino: Mapped[str | None] = mapped_column(String(50), nullable=True)
    severidad: Mapped[SeveridadAviso] = mapped_column(
        Enum(SeveridadAviso, name='severidad_aviso', values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=SeveridadAviso.INFO,
    )
    titulo: Mapped[str] = mapped_column(String(500), nullable=False)
    cuerpo: Mapped[str] = mapped_column(Text, nullable=False)
    inicio_vigencia: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )
    fin_vigencia: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )
    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    requiere_ack: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    __table_args__ = (
        Index('ix_avisos_tenant_activo_vigencia', 'tenant_id', 'activo', 'inicio_vigencia', 'fin_vigencia'),
    )
