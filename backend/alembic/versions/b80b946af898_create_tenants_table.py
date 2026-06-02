"""create_tenants_table

Revision ID: 001
Revises: None
Create Date: 2026-06-02
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.create_table(
        'tenants',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=True),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('codigo', sa.String(50), nullable=False),
        sa.Column('estado', sa.String(20), nullable=False, server_default='Activo'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('codigo', name='uq_tenants_codigo'),
    )
    op.create_index('ix_tenants_codigo', 'tenants', ['codigo'])


def downgrade() -> None:
    op.drop_table('tenants')
