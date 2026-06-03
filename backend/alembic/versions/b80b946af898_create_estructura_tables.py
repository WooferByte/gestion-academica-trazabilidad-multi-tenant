"""create_estructura_tables (carreras, cohortes, materias)

Revision ID: 005
Revises: 004
Create Date: 2026-06-03
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'carreras',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('codigo', sa.String(50), nullable=False),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('estado', sa.String(20), nullable=False, server_default='Activa'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('codigo', 'tenant_id', name='uq_carreras_codigo_tenant'),
    )
    op.create_index('ix_carreras_tenant_id', 'carreras', ['tenant_id'])

    op.create_table(
        'cohortes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('carrera_id', UUID(as_uuid=True), sa.ForeignKey('carreras.id', ondelete='CASCADE'), nullable=False),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('anio', sa.Integer(), nullable=False),
        sa.Column('vig_desde', sa.Date(), nullable=False),
        sa.Column('vig_hasta', sa.Date(), nullable=True),
        sa.Column('estado', sa.String(20), nullable=False, server_default='Activa'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('tenant_id', 'carrera_id', 'nombre', name='uq_cohortes_tenant_carrera_nombre'),
    )
    op.create_index('ix_cohortes_tenant_id', 'cohortes', ['tenant_id'])
    op.create_index('ix_cohortes_carrera_id', 'cohortes', ['carrera_id'])

    op.create_table(
        'materias',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('codigo', sa.String(50), nullable=False),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('estado', sa.String(20), nullable=False, server_default='Activa'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('codigo', 'tenant_id', name='uq_materias_codigo_tenant'),
    )
    op.create_index('ix_materias_tenant_id', 'materias', ['tenant_id'])


def downgrade() -> None:
    op.drop_table('materias')
    op.drop_table('cohortes')
    op.drop_table('carreras')
