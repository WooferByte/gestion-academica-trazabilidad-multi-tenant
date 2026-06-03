"""create_comunicaciones_table

Revision ID: 009
Revises: 008
Create Date: 2026-06-03
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '009'
down_revision: Union[str, None] = '008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'comunicaciones',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('enviado_por', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('materia_id', UUID(as_uuid=True), sa.ForeignKey('materias.id', ondelete='SET NULL'), nullable=True),
        sa.Column('destinatario', sa.Text(), nullable=False),
        sa.Column('asunto', sa.String(500), nullable=False),
        sa.Column('cuerpo', sa.Text(), nullable=False),
        sa.Column('estado', sa.Enum('Pendiente', 'Enviando', 'Enviado', 'Error', 'Cancelado', name='estado_comunicacion'), nullable=False, server_default='Pendiente'),
        sa.Column('lote_id', UUID(as_uuid=True), nullable=False),
        sa.Column('aprobacion_requerida', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('error_msg', sa.Text(), nullable=True),
        sa.Column('programada_para', sa.DateTime(timezone=True), nullable=True),
        sa.Column('enviada_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('aprobada_por', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('cancelada_por', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_comunicaciones_estado_tenant', 'comunicaciones', ['estado', 'tenant_id', 'deleted_at'])
    op.create_index('ix_comunicaciones_lote_tenant', 'comunicaciones', ['lote_id', 'tenant_id'])

    op.add_column(
        'tenants',
        sa.Column('aprobacion_comunicaciones', sa.Boolean(), nullable=False, server_default=sa.text('false')),
    )


def downgrade() -> None:
    op.drop_column('tenants', 'aprobacion_comunicaciones')
    op.drop_table('comunicaciones')
    op.execute('DROP TYPE IF EXISTS estado_comunicacion')
