import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, declared_attr, mapped_column


class BaseModelMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    @declared_attr
    def tenant_id(cls) -> Mapped[uuid.UUID | None]:
        if cls.__name__ == 'Tenant':
            return mapped_column(UUID(as_uuid=True), nullable=True)
        return mapped_column(
            UUID(as_uuid=True),
            ForeignKey('tenants.id', ondelete='CASCADE'),
            nullable=False,
        )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
