"""create_calificaciones_umbral_tables

Revision ID: 008
Revises: 007
Create Date: 2026-06-03
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


revision: str = '008'
down_revision: Union[str, None] = '007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'calificaciones',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('entrada_padron_id', UUID(as_uuid=True), sa.ForeignKey('entrada_padron.id', ondelete='CASCADE'), nullable=False),
        sa.Column('materia_id', UUID(as_uuid=True), sa.ForeignKey('materias.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cohorte_id', UUID(as_uuid=True), sa.ForeignKey('cohortes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('actividad', sa.String(255), nullable=False),
        sa.Column('nota_numerica', sa.Numeric(8, 2), nullable=True),
        sa.Column('nota_textual', sa.String(255), nullable=True),
        sa.Column('origen', sa.String(20), nullable=False, server_default='Importado'),
        sa.Column('importado_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_calificaciones_materia_cohorte', 'calificaciones', ['materia_id', 'cohorte_id'])
    op.create_index('ix_calificaciones_entrada_padron', 'calificaciones', ['entrada_padron_id'])

    op.create_table(
        'umbral_materia',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('asignacion_id', UUID(as_uuid=True), sa.ForeignKey('asignaciones.id', ondelete='CASCADE'), nullable=False),
        sa.Column('materia_id', UUID(as_uuid=True), sa.ForeignKey('materias.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cohorte_id', UUID(as_uuid=True), sa.ForeignKey('cohortes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('umbral_pct', sa.Integer(), nullable=False, server_default=sa.text('60')),
        sa.Column('valores_aprobatorios', JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_umbral_materia_materia_cohorte', 'umbral_materia', ['materia_id', 'cohorte_id'])

    conn = op.get_bind()
    for tenant_row in conn.execute(
        sa.text("SELECT id FROM tenants WHERE deleted_at IS NULL"),
    ):
        tid = tenant_row[0]
        perm_result = conn.execute(
            sa.text(
                "INSERT INTO permisos (tenant_id, codigo, descripcion, modulo, accion, created_at, updated_at) "
                "VALUES (:tid, :codigo, :descripcion, :modulo, :accion, NOW(), NOW()) "
                "ON CONFLICT (codigo, tenant_id) DO NOTHING RETURNING id"
            ),
            {
                'tid': tid,
                'codigo': 'calificaciones:importar',
                'descripcion': 'Importar calificaciones desde archivo',
                'modulo': 'calificaciones',
                'accion': 'importar',
            },
        )
        row = perm_result.fetchone()
        if row:
            perm_id = row[0]
        else:
            existing = conn.execute(
                sa.text("SELECT id FROM permisos WHERE codigo = :codigo AND tenant_id = :tid"),
                {'codigo': 'calificaciones:importar', 'tid': tid},
            ).fetchone()
            perm_id = existing[0] if existing else None

        if perm_id:
            admin_role = conn.execute(
                sa.text("SELECT id FROM roles WHERE codigo = 'ADMIN' AND tenant_id = :tid AND deleted_at IS NULL"),
                {'tid': tid},
            ).fetchone()
            if admin_role:
                conn.execute(
                    sa.text(
                        "INSERT INTO rol_permiso (tenant_id, role_id, permiso_id, propio, created_at, updated_at) "
                        "VALUES (:tid, :role_id, :perm_id, false, NOW(), NOW()) "
                        "ON CONFLICT (role_id, permiso_id, tenant_id) DO NOTHING"
                    ),
                    {'tid': tid, 'role_id': admin_role[0], 'perm_id': perm_id},
                )


def downgrade() -> None:
    op.drop_table('umbral_materia')
    op.drop_table('calificaciones')
