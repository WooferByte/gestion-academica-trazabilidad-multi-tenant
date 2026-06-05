"""create_tareas_tables

Revision ID: 013
Revises: 012
Create Date: 2026-06-05
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '013'
down_revision: Union[str, None] = '012'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'tareas',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('materia_id', UUID(as_uuid=True), sa.ForeignKey('materias.id', ondelete='SET NULL'), nullable=True),
        sa.Column('asignado_a', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('asignado_por', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('estado',
                  sa.Enum('Pendiente', 'En progreso', 'Resuelta', 'Cancelada', name='estado_tarea'),
                  nullable=False, server_default='Pendiente'),
        sa.Column('descripcion', sa.Text, nullable=False),
        sa.Column('contexto_id', UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_tareas_tenant_deleted', 'tareas', ['tenant_id', 'deleted_at'])
    op.create_index('ix_tareas_asignado_a', 'tareas', ['tenant_id', 'asignado_a'])
    op.create_index('ix_tareas_materia_id', 'tareas', ['tenant_id', 'materia_id'])
    op.create_index('ix_tareas_estado', 'tareas', ['tenant_id', 'estado'])

    op.create_table(
        'comentarios_tarea',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tarea_id', UUID(as_uuid=True), sa.ForeignKey('tareas.id', ondelete='CASCADE'), nullable=False),
        sa.Column('autor_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('texto', sa.Text, nullable=False),
        sa.Column('creado_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('comentarios_tarea')
    op.drop_table('tareas')
    op.execute('DROP TYPE IF EXISTS estado_tarea')
