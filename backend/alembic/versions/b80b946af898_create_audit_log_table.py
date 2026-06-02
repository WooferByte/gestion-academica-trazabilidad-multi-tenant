"""create_audit_log_table

Revision ID: 004
Revises: 003
Create Date: 2026-06-02
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'audit_log',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column(
            'tenant_id', UUID(as_uuid=True),
            sa.ForeignKey('tenants.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column(
            'fecha_hora', sa.DateTime(timezone=True),
            server_default=sa.func.now(), nullable=False,
        ),
        sa.Column(
            'actor_id', UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column(
            'impersonado_id', UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='SET NULL'),
            nullable=True,
        ),
        sa.Column('materia_id', UUID(as_uuid=True), nullable=True),
        sa.Column('accion', sa.String(100), nullable=False),
        sa.Column('detalle', JSONB, nullable=True),
        sa.Column('filas_afectadas', sa.Integer, nullable=False, server_default=sa.text('0')),
        sa.Column('ip', sa.String(45), nullable=False),
        sa.Column('user_agent', sa.Text, nullable=False),
    )

    op.create_index('ix_audit_log_tenant_id', 'audit_log', ['tenant_id'])
    op.create_index('ix_audit_log_actor_id', 'audit_log', ['actor_id'])
    op.create_index('ix_audit_log_accion', 'audit_log', ['accion'])
    op.create_index('ix_audit_log_fecha_hora', 'audit_log', ['fecha_hora'])

    op.execute("""
        CREATE OR REPLACE FUNCTION block_audit_log_modification()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION 'audit_log is append-only: UPDATE and DELETE are not allowed';
        END;
        $$ LANGUAGE plpgsql
    """)

    op.execute("""
        CREATE TRIGGER trg_audit_log_append_only
            BEFORE UPDATE OR DELETE ON audit_log
            FOR EACH ROW EXECUTE FUNCTION block_audit_log_modification()
    """)

    # Seed impersonacion:usar permission
    conn = op.get_bind()

    for tenant_row in conn.execute(
        sa.text("SELECT id FROM tenants WHERE deleted_at IS NULL"),
    ):
        tid = tenant_row[0]

        # Insert permission
        perm_result = conn.execute(
            sa.text(
                "INSERT INTO permisos (tenant_id, codigo, descripcion, modulo, accion, created_at, updated_at) "
                "VALUES (:tid, :codigo, :descripcion, :modulo, :accion, NOW(), NOW()) "
                "ON CONFLICT (codigo, tenant_id) DO NOTHING RETURNING id"
            ),
            {
                'tid': tid,
                'codigo': 'impersonacion:usar',
                'descripcion': 'Iniciar sesión de impersonación',
                'modulo': 'impersonacion',
                'accion': 'usar',
            },
        )
        row = perm_result.fetchone()
        if row:
            perm_id = row[0]
        else:
            existing = conn.execute(
                sa.text(
                    "SELECT id FROM permisos WHERE codigo = :codigo AND tenant_id = :tid"
                ),
                {'codigo': 'impersonacion:usar', 'tid': tid},
            ).fetchone()
            if existing:
                perm_id = existing[0]
            else:
                perm_id = None

        if perm_id:
            # Assign to ADMIN role
            admin_role = conn.execute(
                sa.text(
                    "SELECT id FROM roles WHERE codigo = 'ADMIN' AND tenant_id = :tid AND deleted_at IS NULL"
                ),
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
    op.execute("DROP TRIGGER IF EXISTS trg_audit_log_append_only ON audit_log")
    op.execute("DROP FUNCTION IF EXISTS block_audit_log_modification()")
    op.drop_table('audit_log')
