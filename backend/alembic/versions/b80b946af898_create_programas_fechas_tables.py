"""create_programas_fechas_tables

Revision ID: 014
Revises: 013
Create Date: 2026-06-05
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '014'
down_revision: Union[str, None] = '013'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'programas_materia',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('materia_id', UUID(as_uuid=True), sa.ForeignKey('materias.id', ondelete='CASCADE'), nullable=False),
        sa.Column('carrera_id', UUID(as_uuid=True), sa.ForeignKey('carreras.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cohorte_id', UUID(as_uuid=True), sa.ForeignKey('cohortes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('titulo', sa.String(200), nullable=False),
        sa.Column('referencia_archivo', sa.String(500), nullable=True),
        sa.Column('cargado_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('materia_id', 'carrera_id', 'cohorte_id', name='uq_programas_materia_unique'),
    )
    op.create_index('ix_programas_materia_tenant_id', 'programas_materia', ['tenant_id'])
    op.create_index('ix_programas_materia_materia_id', 'programas_materia', ['materia_id'])
    op.create_index('ix_programas_materia_carrera_id', 'programas_materia', ['carrera_id'])
    op.create_index('ix_programas_materia_cohorte_id', 'programas_materia', ['cohorte_id'])

    op.create_table(
        'fechas_academicas',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('materia_id', UUID(as_uuid=True), sa.ForeignKey('materias.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cohorte_id', UUID(as_uuid=True), sa.ForeignKey('cohortes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tipo', sa.String(20), nullable=False),
        sa.Column('numero', sa.Integer(), nullable=False),
        sa.Column('periodo', sa.String(20), nullable=False),
        sa.Column('fecha', sa.Date(), nullable=False),
        sa.Column('titulo', sa.String(200), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_fechas_academicas_tenant_id', 'fechas_academicas', ['tenant_id'])
    op.create_index('ix_fechas_academicas_materia_id', 'fechas_academicas', ['materia_id'])
    op.create_index('ix_fechas_academicas_cohorte_id', 'fechas_academicas', ['cohorte_id'])


def downgrade() -> None:
    op.drop_table('fechas_academicas')
    op.drop_table('programas_materia')
