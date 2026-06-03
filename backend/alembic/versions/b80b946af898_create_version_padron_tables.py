"""create_version_padron_tables

Revision ID: 007
Revises: 006
Create Date: 2026-06-03
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision: str = '007'
down_revision: Union[str, None] = '006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'version_padron',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('materia_id', UUID(as_uuid=True), sa.ForeignKey('materias.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cohorte_id', UUID(as_uuid=True), sa.ForeignKey('cohortes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cargado_por', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cargado_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('activa', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_version_padron_materia_cohorte', 'version_padron', ['materia_id', 'cohorte_id'])
    op.create_index(
        'uq_version_padron_activa_materia_cohorte',
        'version_padron', ['materia_id', 'cohorte_id'],
        unique=True,
        postgresql_where=sa.text('activa = true'),
    )

    op.create_table(
        'entrada_padron',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('version_id', UUID(as_uuid=True), sa.ForeignKey('version_padron.id', ondelete='CASCADE'), nullable=False),
        sa.Column('usuario_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('apellidos', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('comision', sa.String(50), nullable=False),
        sa.Column('regional', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_entrada_padron_version_id', 'entrada_padron', ['version_id'])

    # Seed padron:cargar permission for existing tenants
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
                'codigo': 'padron:cargar',
                'descripcion': 'Cargar y gestionar padrón de alumnos',
                'modulo': 'padron',
                'accion': 'cargar',
            },
        )
        row = perm_result.fetchone()
        if row:
            perm_id = row[0]
        else:
            existing = conn.execute(
                sa.text("SELECT id FROM permisos WHERE codigo = :codigo AND tenant_id = :tid"),
                {'codigo': 'padron:cargar', 'tid': tid},
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
    op.drop_table('entrada_padron')
    op.drop_table('version_padron')
