"""add_user_fields_and_asignaciones

Revision ID: 006
Revises: 005
Create Date: 2026-06-03
"""
import base64
import hashlib
import os
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import Settings

revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _encrypt_email(email: str) -> str:
    settings = Settings()
    aesgcm = AESGCM(settings.encryption_key.encode('utf-8'))
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, email.encode('utf-8'), None)
    return base64.b64encode(nonce + ciphertext).decode('utf-8')


def upgrade() -> None:
    conn = op.get_bind()

    # === 1.1 Add columns to users ===
    op.add_column('users', sa.Column('email_cifrado', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('email_hash', sa.String(64), nullable=True))
    op.add_column('users', sa.Column('dni_hash', sa.String(64), nullable=True))
    op.add_column('users', sa.Column('cuil_cifrado', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('cbu_cifrado', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('alias_cbu_cifrado', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('banco', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('regional', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('legajo', sa.String(50), nullable=True))
    op.add_column('users', sa.Column('legajo_profesional', sa.String(50), nullable=True))
    op.add_column('users', sa.Column('facturador', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('users', sa.Column('estado', sa.String(20), nullable=False, server_default='Activo'))

    # Migrate existing emails: encrypt and hash
    email_hash_salt = 'activia-trace-email-hash-salt-dev'
    rows = conn.execute(
        sa.text("SELECT id, email FROM users WHERE deleted_at IS NULL"),
    ).fetchall()

    for row in rows:
        uid, email = row
        normalized = email.strip().lower()
        email_hash_val = hashlib.sha256(
            (normalized + email_hash_salt).encode()
        ).hexdigest()

        ciphertext = _encrypt_email(email)
        conn.execute(
            sa.text(
                "UPDATE users SET email_cifrado = :cifrado, email_hash = :hash "
                "WHERE id = :uid"
            ),
            {'cifrado': ciphertext, 'hash': email_hash_val, 'uid': uid},
        )

    # Make columns NOT NULL after migration
    op.alter_column('users', 'email_cifrado', nullable=False)
    op.alter_column('users', 'email_hash', nullable=False)

    # Unique indexes
    op.create_unique_constraint(
        'uq_users_email_hash_tenant', 'users', ['tenant_id', 'email_hash'],
    )
    op.create_unique_constraint(
        'uq_users_dni_hash_tenant', 'users', ['tenant_id', 'dni_hash'],
    )
    op.create_index('ix_users_email_hash', 'users', ['email_hash'])

    # === 1.2 Create asignaciones table ===
    op.create_table(
        'asignaciones',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('usuario_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('rol', sa.String(50), nullable=False),
        sa.Column('materia_id', UUID(as_uuid=True), sa.ForeignKey('materias.id', ondelete='SET NULL'), nullable=True),
        sa.Column('carrera_id', UUID(as_uuid=True), sa.ForeignKey('carreras.id', ondelete='SET NULL'), nullable=True),
        sa.Column('cohorte_id', UUID(as_uuid=True), sa.ForeignKey('cohortes.id', ondelete='SET NULL'), nullable=True),
        sa.Column('comisiones', JSONB, nullable=True),
        sa.Column('responsable_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('desde', sa.DateTime(timezone=True), nullable=True),
        sa.Column('hasta', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_asignaciones_usuario_id', 'asignaciones', ['usuario_id'])
    op.create_index('ix_asignaciones_rol', 'asignaciones', ['rol'])
    op.create_index('ix_asignaciones_materia_id', 'asignaciones', ['materia_id'])
    op.create_index('ix_asignaciones_responsable_id', 'asignaciones', ['responsable_id'])

    # === 1.3 Seed new permissions ===
    for tenant_row in conn.execute(
        sa.text("SELECT id FROM tenants WHERE deleted_at IS NULL"),
    ):
        tid = tenant_row[0]

        # Add usuarios:gestionar permission
        perm_result = conn.execute(
            sa.text(
                "INSERT INTO permisos (tenant_id, codigo, descripcion, modulo, accion, created_at, updated_at) "
                "VALUES (:tid, :codigo, :descripcion, :modulo, :accion, NOW(), NOW()) "
                "ON CONFLICT (codigo, tenant_id) DO NOTHING RETURNING id"
            ),
            {
                'tid': tid,
                'codigo': 'usuarios:gestionar',
                'descripcion': 'Gestionar usuarios del tenant',
                'modulo': 'usuarios',
                'accion': 'gestionar',
            },
        )
        row = perm_result.fetchone()
        if row:
            perm_id = row[0]
        else:
            existing = conn.execute(
                sa.text("SELECT id FROM permisos WHERE codigo = :codigo AND tenant_id = :tid"),
                {'codigo': 'usuarios:gestionar', 'tid': tid},
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
    op.drop_table('asignaciones')
    op.drop_constraint('uq_users_email_hash_tenant', 'users', type_='unique')
    op.drop_constraint('uq_users_dni_hash_tenant', 'users', type_='unique')
    op.drop_index('ix_users_email_hash', table_name='users')
    op.drop_column('users', 'estado')
    op.drop_column('users', 'facturador')
    op.drop_column('users', 'legajo_profesional')
    op.drop_column('users', 'legajo')
    op.drop_column('users', 'regional')
    op.drop_column('users', 'banco')
    op.drop_column('users', 'alias_cbu_cifrado')
    op.drop_column('users', 'cbu_cifrado')
    op.drop_column('users', 'cuil_cifrado')
    op.drop_column('users', 'dni_hash')
    op.drop_column('users', 'email_hash')
    op.drop_column('users', 'email_cifrado')
