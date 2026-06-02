import uuid
from datetime import datetime

from sqlalchemy import DDL, DateTime, ForeignKey, Integer, String, Text, event, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = 'audit_log'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('tenants.id', ondelete='CASCADE'),
        nullable=False,
    )
    fecha_hora: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    actor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    impersonado_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
    )
    materia_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True,
    )
    accion: Mapped[str] = mapped_column(String(100), nullable=False)
    detalle: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    filas_afectadas: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
    )
    ip: Mapped[str] = mapped_column(String(45), nullable=False)
    user_agent: Mapped[str] = mapped_column(Text, nullable=False)


_audit_trigger_func = DDL("""
    CREATE OR REPLACE FUNCTION block_audit_log_modification()
    RETURNS TRIGGER AS $$
    BEGIN
        RAISE EXCEPTION 'audit_log is append-only: UPDATE and DELETE are not allowed';
    END;
    $$ LANGUAGE plpgsql
""")

_audit_trigger_apply = DDL("""
    CREATE TRIGGER trg_audit_log_append_only
        BEFORE UPDATE OR DELETE ON audit_log
        FOR EACH ROW EXECUTE FUNCTION block_audit_log_modification()
""")

event.listen(AuditLog.__table__, 'after_create', _audit_trigger_func)
event.listen(AuditLog.__table__, 'after_create', _audit_trigger_apply)
