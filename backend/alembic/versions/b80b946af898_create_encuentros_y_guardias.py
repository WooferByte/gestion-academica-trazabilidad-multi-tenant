"""create_encuentros_y_guardias

Revision ID: 010
Revises: 009
Create Date: 2026-06-03
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '010'
down_revision: Union[str, None] = '009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'slots_encuentro',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('asignacion_id', UUID(as_uuid=True), sa.ForeignKey('asignaciones.id', ondelete='CASCADE'), nullable=False),
        sa.Column('materia_id', UUID(as_uuid=True), sa.ForeignKey('materias.id', ondelete='CASCADE'), nullable=False),
        sa.Column('titulo', sa.String(255), nullable=False),
        sa.Column('hora', sa.String(5), nullable=False),
        sa.Column('dia_semana',
                  sa.Enum('Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo',
                          name='dia_semana'),
                  nullable=False),
        sa.Column('fecha_inicio', sa.Date(), nullable=False),
        sa.Column('cant_semanas', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('fecha_unica', sa.Date(), nullable=True),
        sa.Column('meet_url', sa.String(500), nullable=True),
        sa.Column('vig_desde', sa.Date(), nullable=True),
        sa.Column('vig_hasta', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_slots_encuentro_materia', 'slots_encuentro', ['materia_id', 'tenant_id'])

    op.create_table(
        'instancias_encuentro',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('slot_id', UUID(as_uuid=True), sa.ForeignKey('slots_encuentro.id', ondelete='SET NULL'), nullable=True),
        sa.Column('materia_id', UUID(as_uuid=True), sa.ForeignKey('materias.id', ondelete='CASCADE'), nullable=False),
        sa.Column('fecha', sa.Date(), nullable=False),
        sa.Column('hora', sa.String(5), nullable=False),
        sa.Column('titulo', sa.String(255), nullable=False),
        sa.Column('estado',
                  sa.Enum('Programado', 'Realizado', 'Cancelado', name='estado_instancia'),
                  nullable=False, server_default='Programado'),
        sa.Column('meet_url', sa.String(500), nullable=True),
        sa.Column('video_url', sa.String(500), nullable=True),
        sa.Column('comentario', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_instancias_materia_fecha', 'instancias_encuentro', ['materia_id', 'fecha', 'tenant_id'])
    op.create_index('ix_instancias_slot_id', 'instancias_encuentro', ['slot_id'])

    op.create_table(
        'guardias',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('asignacion_id', UUID(as_uuid=True), sa.ForeignKey('asignaciones.id', ondelete='CASCADE'), nullable=False),
        sa.Column('materia_id', UUID(as_uuid=True), sa.ForeignKey('materias.id', ondelete='CASCADE'), nullable=False),
        sa.Column('carrera_id', UUID(as_uuid=True), sa.ForeignKey('carreras.id', ondelete='SET NULL'), nullable=True),
        sa.Column('cohorte_id', UUID(as_uuid=True), sa.ForeignKey('cohortes.id', ondelete='SET NULL'), nullable=True),
        sa.Column('dia',
                  sa.Enum('Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo',
                          name='dia_semana'),
                  nullable=False),
        sa.Column('horario', sa.String(20), nullable=False),
        sa.Column('estado',
                  sa.Enum('Pendiente', 'Realizada', 'Cancelada', name='estado_guardia'),
                  nullable=False, server_default='Pendiente'),
        sa.Column('comentarios', sa.Text(), nullable=True),
        sa.Column('creada_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_guardias_materia', 'guardias', ['materia_id', 'tenant_id'])
    op.create_index('ix_guardias_asignacion', 'guardias', ['asignacion_id', 'tenant_id'])


def downgrade() -> None:
    op.drop_table('guardias')
    op.drop_table('instancias_encuentro')
    op.drop_table('slots_encuentro')
    op.execute('DROP TYPE IF EXISTS estado_guardia')
    op.execute('DROP TYPE IF EXISTS estado_instancia')
    op.execute('DROP TYPE IF EXISTS dia_semana')
