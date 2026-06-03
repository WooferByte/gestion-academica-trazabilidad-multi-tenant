"""create_avisos_tables

Revision ID: 012
Revises: 011
Create Date: 2026-06-03
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '012'
down_revision: Union[str, None] = '011'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'avisos',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('alcance',
                  sa.Enum('Global', 'PorMateria', 'PorCohorte', 'PorRol', name='alcance_aviso'),
                  nullable=False),
        sa.Column('materia_id', UUID(as_uuid=True), sa.ForeignKey('materias.id', ondelete='SET NULL'), nullable=True),
        sa.Column('cohorte_id', UUID(as_uuid=True), sa.ForeignKey('cohortes.id', ondelete='SET NULL'), nullable=True),
        sa.Column('rol_destino', sa.String(50), nullable=True),
        sa.Column('severidad',
                  sa.Enum('Info', 'Advertencia', 'Crítico', name='severidad_aviso'),
                  nullable=False, server_default='Info'),
        sa.Column('titulo', sa.String(500), nullable=False),
        sa.Column('cuerpo', sa.Text, nullable=False),
        sa.Column('inicio_vigencia', sa.DateTime(timezone=True), nullable=False),
        sa.Column('fin_vigencia', sa.DateTime(timezone=True), nullable=False),
        sa.Column('orden', sa.Integer, nullable=False, server_default=sa.text('0')),
        sa.Column('activo', sa.Boolean, nullable=False, server_default=sa.text('true')),
        sa.Column('requiere_ack', sa.Boolean, nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_avisos_tenant_activo_vigencia', 'avisos', ['tenant_id', 'activo', 'inicio_vigencia', 'fin_vigencia'])

    op.create_table(
        'acknowledgment_avisos',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('aviso_id', UUID(as_uuid=True), sa.ForeignKey('avisos.id', ondelete='CASCADE'), nullable=False),
        sa.Column('usuario_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('confirmado_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('aviso_id', 'usuario_id', name='uq_ack_aviso_usuario'),
    )
    op.create_index('ix_ack_aviso', 'acknowledgment_avisos', ['aviso_id'])
    op.create_index('ix_ack_usuario', 'acknowledgment_avisos', ['usuario_id'])


def downgrade() -> None:
    op.drop_table('acknowledgment_avisos')
    op.drop_table('avisos')
    op.execute('DROP TYPE IF EXISTS alcance_aviso')
    op.execute('DROP TYPE IF EXISTS severidad_aviso')
