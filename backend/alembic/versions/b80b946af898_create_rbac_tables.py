"""create_rbac_tables

Revision ID: 003
Revises: 002
Create Date: 2026-06-02
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'roles',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('codigo', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('codigo', 'tenant_id', name='uq_roles_codigo_tenant'),
    )

    op.create_table(
        'permisos',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('codigo', sa.String(100), nullable=False),
        sa.Column('descripcion', sa.String(255), nullable=True),
        sa.Column('modulo', sa.String(50), nullable=False),
        sa.Column('accion', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('codigo', 'tenant_id', name='uq_permisos_codigo_tenant'),
    )

    op.create_table(
        'rol_permiso',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role_id', UUID(as_uuid=True), sa.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('permiso_id', UUID(as_uuid=True), sa.ForeignKey('permisos.id', ondelete='CASCADE'), nullable=False),
        sa.Column('propio', sa.Boolean, nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('role_id', 'permiso_id', 'tenant_id', name='uq_rol_permiso'),
    )

    op.create_table(
        'user_roles',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role_id', UUID(as_uuid=True), sa.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('desde', sa.DateTime(timezone=True), nullable=True),
        sa.Column('hasta', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('user_id', 'role_id', 'tenant_id', name='uq_user_roles'),
    )

    # === SEED DATA ===
    # Get default tenant (first tenant)
    conn = op.get_bind()

    # Seed roles
    roles_data = [
        ('ALUMNO', 'ALUMNO'),
        ('TUTOR', 'TUTOR'),
        ('PROFESOR', 'PROFESOR'),
        ('COORDINADOR', 'COORDINADOR'),
        ('NEXO', 'NEXO'),
        ('ADMIN', 'ADMIN'),
        ('FINANZAS', 'FINANZAS'),
    ]

    for tenant_row in conn.execute(sa.text("SELECT id FROM tenants WHERE deleted_at IS NULL")):
        tid = tenant_row[0]

        role_ids = {}
        for name, codigo in roles_data:
            result = conn.execute(
                sa.text(
                    "INSERT INTO roles (tenant_id, name, codigo, created_at, updated_at) "
                    "VALUES (:tid, :name, :codigo, NOW(), NOW()) "
                    "ON CONFLICT (codigo, tenant_id) DO NOTHING RETURNING id"
                ),
                {'tid': tid, 'name': name, 'codigo': codigo},
            )
            row = result.fetchone()
            if row:
                role_ids[codigo] = row[0]
            else:
                existing = conn.execute(
                    sa.text("SELECT id FROM roles WHERE codigo = :codigo AND tenant_id = :tid"),
                    {'codigo': codigo, 'tid': tid},
                ).fetchone()
                if existing:
                    role_ids[codigo] = existing[0]

        # Seed permissions
        permisos_data = [
            ('ver_estado_academico_propio', 'Ver estado académico propio', 'calificaciones', 'ver_propio'),
            ('reservar_evaluacion', 'Reservar instancia de evaluación', 'evaluaciones', 'reservar'),
            ('confirmar_avisos', 'Confirmar avisos (acknowledgment)', 'comunicacion', 'confirmar'),
            ('calificaciones:importar', 'Importar calificaciones', 'calificaciones', 'importar'),
            ('atrasados:ver', 'Ver alumnos atrasados', 'atrasados', 'ver'),
            ('entregas:detectar_sin_corregir', 'Detectar entregas sin corregir', 'entregas', 'detectar_sin_corregir'),
            ('comunicacion:enviar', 'Enviar comunicaciones a alumnos', 'comunicacion', 'enviar'),
            ('comunicacion:aprobar', 'Aprobar comunicaciones masivas', 'comunicacion', 'aprobar'),
            ('encuentros:gestionar', 'Gestionar encuentros', 'encuentros', 'gestionar'),
            ('guardias:registrar', 'Registrar guardias', 'guardias', 'registrar'),
            ('tareas:gestionar', 'Gestionar tareas internas', 'tareas', 'gestionar'),
            ('avisos:publicar', 'Publicar avisos', 'avisos', 'publicar'),
            ('equipos:asignar', 'Gestionar equipos docentes', 'equipos', 'asignar'),
            ('gestionar_estructura_academica', 'Gestionar estructura académica', 'estructura', 'gestionar'),
            ('gestionar_usuarios', 'Gestionar usuarios del tenant', 'usuarios', 'gestionar'),
            ('ver_auditoria', 'Ver auditoría', 'auditoria', 'ver'),
            ('operar_grilla_salarial', 'Operar grilla salarial', 'liquidaciones', 'operar_grilla'),
            ('calcular_liquidaciones', 'Calcular / cerrar liquidaciones', 'liquidaciones', 'calcular'),
            ('gestionar_facturas', 'Gestionar facturas', 'liquidaciones', 'gestionar_facturas'),
            ('configurar_tenant', 'Configurar el tenant', 'configuracion', 'configurar'),
            ('rbac:gestionar', 'Gestionar roles y permisos', 'rbac', 'gestionar'),
        ]

        permiso_ids = {}
        for codigo, descripcion, modulo, accion in permisos_data:
            result = conn.execute(
                sa.text(
                    "INSERT INTO permisos (tenant_id, codigo, descripcion, modulo, accion, created_at, updated_at) "
                    "VALUES (:tid, :codigo, :descripcion, :modulo, :accion, NOW(), NOW()) "
                    "ON CONFLICT (codigo, tenant_id) DO NOTHING RETURNING id"
                ),
                {'tid': tid, 'codigo': codigo, 'descripcion': descripcion, 'modulo': modulo, 'accion': accion},
            )
            row = result.fetchone()
            if row:
                permiso_ids[codigo] = row[0]
            else:
                existing = conn.execute(
                    sa.text("SELECT id FROM permisos WHERE codigo = :codigo AND tenant_id = :tid"),
                    {'codigo': codigo, 'tid': tid},
                ).fetchone()
                if existing:
                    permiso_ids[codigo] = existing[0]

        # Seed role-permission matrix (from 03_actores_y_roles.md §3.3)
        matrix = {
            'ALUMNO': [
                ('ver_estado_academico_propio', False),
                ('reservar_evaluacion', False),
                ('confirmar_avisos', False),
            ],
            'TUTOR': [
                ('confirmar_avisos', False),
                ('atrasados:ver', False),
                ('entregas:detectar_sin_corregir', False),
                ('encuentros:gestionar', False),
                ('guardias:registrar', True),
            ],
            'PROFESOR': [
                ('confirmar_avisos', False),
                ('calificaciones:importar', True),
                ('atrasados:ver', True),
                ('entregas:detectar_sin_corregir', True),
                ('comunicacion:enviar', True),
                ('encuentros:gestionar', True),
                ('guardias:registrar', True),
                ('tareas:gestionar', True),
            ],
            'COORDINADOR': [
                ('confirmar_avisos', False),
                ('calificaciones:importar', False),
                ('atrasados:ver', False),
                ('entregas:detectar_sin_corregir', False),
                ('comunicacion:enviar', False),
                ('comunicacion:aprobar', False),
                ('encuentros:gestionar', False),
                ('guardias:registrar', False),
                ('tareas:gestionar', False),
                ('avisos:publicar', False),
                ('equipos:asignar', False),
                ('ver_auditoria', True),
            ],
            'NEXO': [
                ('confirmar_avisos', False),
            ],
            'ADMIN': [
                ('confirmar_avisos', False),
                ('calificaciones:importar', False),
                ('atrasados:ver', False),
                ('entregas:detectar_sin_corregir', False),
                ('comunicacion:enviar', False),
                ('comunicacion:aprobar', False),
                ('encuentros:gestionar', False),
                ('guardias:registrar', False),
                ('tareas:gestionar', False),
                ('avisos:publicar', False),
                ('equipos:asignar', False),
                ('gestionar_estructura_academica', False),
                ('gestionar_usuarios', False),
                ('ver_auditoria', False),
                ('configurar_tenant', False),
                ('rbac:gestionar', False),
            ],
            'FINANZAS': [
                ('confirmar_avisos', False),
                ('ver_auditoria', False),
                ('operar_grilla_salarial', False),
                ('calcular_liquidaciones', False),
                ('gestionar_facturas', False),
            ],
        }

        for role_codigo, perms in matrix.items():
            role_id = role_ids.get(role_codigo)
            if not role_id:
                continue
            for perm_codigo, propio in perms:
                perm_id = permiso_ids.get(perm_codigo)
                if not perm_id:
                    continue
                conn.execute(
                    sa.text(
                        "INSERT INTO rol_permiso (tenant_id, role_id, permiso_id, propio, created_at, updated_at) "
                        "VALUES (:tid, :role_id, :perm_id, :propio, NOW(), NOW()) "
                        "ON CONFLICT (role_id, permiso_id, tenant_id) DO NOTHING"
                    ),
                    {'tid': tid, 'role_id': role_id, 'perm_id': perm_id, 'propio': propio},
                )

        # Data migration: copy User.roles JSONB to user_roles
        users_rows = conn.execute(
            sa.text(
                "SELECT id, tenant_id, roles FROM users "
                "WHERE deleted_at IS NULL AND roles IS NOT NULL AND roles != '[]'::jsonb"
            ),
        ).fetchall()

        for user_row in users_rows:
            uid, user_tid, roles_json = user_row
            if not roles_json:
                continue
            role_codigos = list(roles_json) if isinstance(roles_json, list) else []
            for role_codigo in role_codigos:
                rid = role_ids.get(role_codigo)
                if not rid:
                    continue
                conn.execute(
                    sa.text(
                        "INSERT INTO user_roles (tenant_id, user_id, role_id, created_at, updated_at) "
                        "VALUES (:tid, :uid, :rid, NOW(), NOW()) "
                        "ON CONFLICT (user_id, role_id, tenant_id) DO NOTHING"
                    ),
                    {'tid': user_tid, 'uid': uid, 'rid': rid},
                )


def downgrade() -> None:
    op.drop_table('user_roles')
    op.drop_table('rol_permiso')
    op.drop_table('permisos')
    op.drop_table('roles')
