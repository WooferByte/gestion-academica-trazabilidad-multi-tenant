import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class User(Base, BaseModelMixin):
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre_cifrado: Mapped[str | None] = mapped_column(Text, nullable=True)
    apellido_cifrado: Mapped[str | None] = mapped_column(Text, nullable=True)
    dni_cifrado: Mapped[str | None] = mapped_column(Text, nullable=True)
    roles: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    totp_secret_cifrado: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    refresh_tokens: Mapped[list['RefreshToken']] = relationship(
        back_populates='user', cascade='all, delete-orphan',
    )
    password_reset_tokens: Mapped[list['PasswordResetToken']] = relationship(
        back_populates='user', cascade='all, delete-orphan',
    )

    __table_args__ = (
        UniqueConstraint('email', 'tenant_id', name='uq_users_email_tenant'),
        Index('ix_users_email', 'email'),
    )


class RefreshToken(Base, BaseModelMixin):
    __tablename__ = 'refresh_tokens'

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    family_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    user: Mapped['User'] = relationship(back_populates='refresh_tokens')

    __table_args__ = (
        Index('ix_refresh_tokens_token_hash', 'token_hash'),
        Index('ix_refresh_tokens_family_id', 'family_id'),
    )


class PasswordResetToken(Base, BaseModelMixin):
    __tablename__ = 'password_reset_tokens'

    token_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )
    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    user: Mapped['User'] = relationship(back_populates='password_reset_tokens')

    __table_args__ = (
        Index('ix_password_reset_tokens_token_hash', 'token_hash'),
    )
