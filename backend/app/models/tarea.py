import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class EstadoTarea(str, enum.Enum):
    PENDIENTE = 'Pendiente'
    EN_PROGRESO = 'En progreso'
    RESUELTA = 'Resuelta'
    CANCELADA = 'Cancelada'


class Tarea(Base, BaseModelMixin):
    __tablename__ = 'tareas'

    materia_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('materias.id', ondelete='SET NULL'), nullable=True,
    )
    asignado_a: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False,
    )
    asignado_por: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False,
    )
    estado: Mapped[EstadoTarea] = mapped_column(
        Enum(EstadoTarea, name='estado_tarea', values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=EstadoTarea.PENDIENTE,
    )
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    contexto_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True,
    )

    __table_args__ = (
        Index('ix_tareas_tenant_deleted', 'tenant_id', 'deleted_at'),
        Index('ix_tareas_asignado_a', 'tenant_id', 'asignado_a'),
        Index('ix_tareas_materia_id', 'tenant_id', 'materia_id'),
        Index('ix_tareas_estado', 'tenant_id', 'estado'),
    )


class ComentarioTarea(Base, BaseModelMixin):
    __tablename__ = 'comentarios_tarea'

    tarea_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('tareas.id', ondelete='CASCADE'), nullable=False,
    )
    autor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False,
    )
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    creado_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False,
    )
