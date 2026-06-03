"""create_evaluaciones_tables

Revision ID: 011
Revises: 010
Create Date: 2026-06-03
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '011'
down_revision: Union[str, None] = '010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'evaluaciones',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('materia_id', UUID(as_uuid=True), sa.ForeignKey('materias.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cohorte_id', UUID(as_uuid=True), sa.ForeignKey('cohortes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tipo',
                  sa.Enum('Parcial', 'Recuperatorio', 'Coloquio', 'TP', name='tipo_evaluacion'),
                  nullable=False),
        sa.Column('instancia', sa.String(255), nullable=False),
        sa.Column('estado',
                  sa.Enum('Activa', 'Cerrada', name='estado_evaluacion'),
                  nullable=False, server_default='Activa'),
        sa.Column('dias_disponibles', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_evaluaciones_materia', 'evaluaciones', ['materia_id', 'tenant_id'])
    op.create_index('ix_evaluaciones_cohorte', 'evaluaciones', ['cohorte_id', 'tenant_id'])

    op.create_table(
        'turnos_coloquio',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('evaluacion_id', UUID(as_uuid=True), sa.ForeignKey('evaluaciones.id', ondelete='CASCADE'), nullable=False),
        sa.Column('fecha', sa.Date(), nullable=False),
        sa.Column('hora_inicio', sa.Time(), nullable=False),
        sa.Column('hora_fin', sa.Time(), nullable=False),
        sa.Column('cupo', sa.Integer(), nullable=False),
        sa.Column('ocupados', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_turnos_evaluacion', 'turnos_coloquio', ['evaluacion_id', 'tenant_id'])
    op.create_check_constraint('ck_turno_ocupados_positivo', 'turnos_coloquio', 'ocupados >= 0')
    op.create_check_constraint('ck_turno_ocupados_no_excede_cupo', 'turnos_coloquio', 'ocupados <= cupo')
    op.create_check_constraint('ck_turno_cupo_positivo', 'turnos_coloquio', 'cupo >= 0')

    op.create_table(
        'reservas_evaluacion',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('turno_id', UUID(as_uuid=True), sa.ForeignKey('turnos_coloquio.id', ondelete='CASCADE'), nullable=False),
        sa.Column('alumno_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('evaluacion_id', UUID(as_uuid=True), sa.ForeignKey('evaluaciones.id', ondelete='CASCADE'), nullable=False),
        sa.Column('estado',
                  sa.Enum('Activa', 'Cancelada', name='estado_reserva'),
                  nullable=False, server_default='Activa'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_reservas_alumno', 'reservas_evaluacion', ['alumno_id', 'tenant_id'])
    op.create_index('ix_reservas_evaluacion', 'reservas_evaluacion', ['evaluacion_id', 'tenant_id'])
    op.create_unique_constraint('uq_reserva_turno_alumno', 'reservas_evaluacion', ['turno_id', 'alumno_id'])

    op.create_table(
        'resultados_evaluacion',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('evaluacion_id', UUID(as_uuid=True), sa.ForeignKey('evaluaciones.id', ondelete='CASCADE'), nullable=False),
        sa.Column('alumno_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('nota_final', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_resultados_evaluacion', 'resultados_evaluacion', ['evaluacion_id', 'tenant_id'])
    op.create_unique_constraint('uq_resultado_evaluacion_alumno', 'resultados_evaluacion', ['evaluacion_id', 'alumno_id'])

    op.create_table(
        'coloquio_alumnos',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('evaluacion_id', UUID(as_uuid=True), sa.ForeignKey('evaluaciones.id', ondelete='CASCADE'), nullable=False),
        sa.Column('alumno_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_coloquio_alumnos_evaluacion', 'coloquio_alumnos', ['evaluacion_id', 'tenant_id'])
    op.create_index('ix_coloquio_alumnos_alumno', 'coloquio_alumnos', ['alumno_id', 'tenant_id'])
    op.create_unique_constraint('uq_coloquio_alumno', 'coloquio_alumnos', ['evaluacion_id', 'alumno_id'])


def downgrade() -> None:
    op.drop_table('coloquio_alumnos')
    op.drop_table('resultados_evaluacion')
    op.drop_table('reservas_evaluacion')
    op.drop_table('turnos_coloquio')
    op.drop_table('evaluaciones')
    op.execute('DROP TYPE IF EXISTS estado_reserva')
    op.execute('DROP TYPE IF EXISTS estado_evaluacion')
    op.execute('DROP TYPE IF EXISTS tipo_evaluacion')
