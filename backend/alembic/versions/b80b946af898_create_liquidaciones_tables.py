"""create_liquidaciones_tables

Revision ID: 014
Revises: 013
Create Date: 2026-06-06
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
    # ── 1. Categorias Plus (seed reference table) ──────────────────────────
    op.create_table(
        'categorias_plus',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('codigo', sa.String(20), nullable=False),
        sa.Column('nombre', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('codigo', 'tenant_id', name='uq_categorias_plus_codigo_tenant'),
    )

    # ── 2. Salarios Base ──────────────────────────────────────────────────
    op.create_table(
        'salarios_base',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('rol', sa.String(50), nullable=False),
        sa.Column('monto', sa.Numeric(12, 2), nullable=False),
        sa.Column('desde', sa.Date(), nullable=False),
        sa.Column('hasta', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_salarios_base_rol_vigencia', 'salarios_base', ['rol', 'desde', 'hasta'])

    # ── 3. Salarios Plus ──────────────────────────────────────────────────
    op.create_table(
        'salarios_plus',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('grupo', sa.String(20), nullable=False),
        sa.Column('rol', sa.String(50), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('monto', sa.Numeric(12, 2), nullable=False),
        sa.Column('desde', sa.Date(), nullable=False),
        sa.Column('hasta', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_salarios_plus_grupo_rol_vigencia', 'salarios_plus', ['grupo', 'rol', 'desde', 'hasta'])

    # ── 4. Liquidaciones ──────────────────────────────────────────────────
    op.create_table(
        'liquidaciones',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('usuario_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cohorte_id', UUID(as_uuid=True), sa.ForeignKey('cohortes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('periodo', sa.String(7), nullable=False),
        sa.Column('rol', sa.String(50), nullable=False),
        sa.Column('monto_base', sa.Numeric(12, 2), nullable=False),
        sa.Column('monto_plus', sa.Numeric(12, 2), nullable=False, server_default=sa.text('0')),
        sa.Column('total', sa.Numeric(12, 2), nullable=False),
        sa.Column('es_nexo', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('excluido_por_factura', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('estado', sa.String(20), nullable=False, server_default='Abierta'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_liquidaciones_cohorte_periodo', 'liquidaciones', ['cohorte_id', 'periodo'])
    op.create_index('ix_liquidaciones_usuario', 'liquidaciones', ['usuario_id'])
    op.create_index('ix_liquidaciones_estado', 'liquidaciones', ['estado'])

    # ── 5. Facturas ───────────────────────────────────────────────────────
    op.create_table(
        'facturas',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('usuario_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('periodo', sa.String(7), nullable=False),
        sa.Column('detalle', sa.Text(), nullable=False),
        sa.Column('referencia_archivo', sa.String(500), nullable=True),
        sa.Column('tamano_kb', sa.Numeric(10, 2), nullable=True),
        sa.Column('estado', sa.String(20), nullable=False, server_default='Pendiente'),
        sa.Column('cargada_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('abonada_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_facturas_usuario_periodo', 'facturas', ['usuario_id', 'periodo'])
    op.create_index('ix_facturas_estado', 'facturas', ['estado'])

    # ── 6. Add categoria column to materias ───────────────────────────────
    op.add_column('materias', sa.Column('categoria', sa.String(20), nullable=True))

    # ── 7. Seed categorias_plus for each existing tenant ───────────────────
    conn = op.get_bind()
    categorias = [
        ('PROG', 'Programación'),
        ('BD', 'Bases de Datos'),
        ('ING_SOFT', 'Ingeniería de Software'),
        ('SIST_OP', 'Sistemas Operativos'),
        ('MAT', 'Matemática'),
        ('HW', 'Hardware'),
        ('N_A', 'Sin categoría'),
    ]
    for tenant_row in conn.execute(
        sa.text("SELECT id FROM tenants WHERE deleted_at IS NULL"),
    ):
        tid = tenant_row[0]
        for codigo, nombre in categorias:
            conn.execute(
                sa.text(
                    "INSERT INTO categorias_plus (tenant_id, codigo, nombre, created_at, updated_at) "
                    "VALUES (:tid, :codigo, :nombre, NOW(), NOW()) "
                    "ON CONFLICT (codigo, tenant_id) DO NOTHING"
                ),
                {'tid': tid, 'codigo': codigo, 'nombre': nombre},
            )

    # ── 8. Seed liquidacion permissions for FINANZAS role ──────────────────
    for tenant_row in conn.execute(
        sa.text("SELECT id FROM tenants WHERE deleted_at IS NULL"),
    ):
        tid = tenant_row[0]
        permisos_liquidaciones = [
            ('liquidaciones:ver', 'liquidaciones', 'ver'),
            ('liquidaciones:calcular', 'liquidaciones', 'calcular'),
            ('liquidaciones:cerrar', 'liquidaciones', 'cerrar'),
            ('liquidaciones:exportar', 'liquidaciones', 'exportar'),
            ('liquidaciones:configurar-salarios', 'liquidaciones', 'configurar-salarios'),
            ('facturas:gestionar', 'facturas', 'gestionar'),
        ]
        for codigo, modulo, accion in permisos_liquidaciones:
            perm_result = conn.execute(
                sa.text(
                    "INSERT INTO permisos (tenant_id, codigo, descripcion, modulo, accion, created_at, updated_at) "
                    "VALUES (:tid, :codigo, :descripcion, :modulo, :accion, NOW(), NOW()) "
                    "ON CONFLICT (codigo, tenant_id) DO NOTHING RETURNING id"
                ),
                {
                    'tid': tid,
                    'codigo': codigo,
                    'descripcion': f'{modulo}:{accion}',
                    'modulo': modulo,
                    'accion': accion,
                },
            )
            row = perm_result.fetchone()
            if row:
                perm_id = row[0]
            else:
                existing = conn.execute(
                    sa.text("SELECT id FROM permisos WHERE codigo = :codigo AND tenant_id = :tid"),
                    {'codigo': codigo, 'tid': tid},
                ).fetchone()
                perm_id = existing[0] if existing else None

            if perm_id:
                # Assign to ADMIN role
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
    op.drop_table('facturas')
    op.drop_table('liquidaciones')
    op.drop_table('salarios_plus')
    op.drop_table('salarios_base')
    op.drop_table('categorias_plus')
    op.drop_column('materias', 'categoria')
