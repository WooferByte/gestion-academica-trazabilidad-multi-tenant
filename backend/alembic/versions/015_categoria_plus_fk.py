"""migrate materia.categoria string to categoria_plus_id FK

Revision ID: 015
Revises: 014
Create Date: 2026-06-06
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = '015'
down_revision: Union[str, None] = '014'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Add nullable categoria_plus_id FK
    op.add_column(
        'materias',
        sa.Column('categoria_plus_id', UUID(as_uuid=True), sa.ForeignKey('categorias_plus.id'), nullable=True),
    )

    # 2. Migrate existing string categoria to FK reference
    # For each materia with a categoria string, find matching CategoriaPlus by codigo
    categorias_plus = {}
    for row in conn.execute(
        sa.text("SELECT id, codigo, tenant_id FROM categorias_plus WHERE deleted_at IS NULL"),
    ):
        key = (row.codigo, row.tenant_id)
        categorias_plus[key] = row.id

    materias = conn.execute(
        sa.text("SELECT id, categoria, tenant_id FROM materias WHERE categoria IS NOT NULL AND deleted_at IS NULL"),
    )
    for m_row in materias:
        mid, cat_str, tid = m_row
        cp_id = categorias_plus.get((cat_str, tid))
        if cp_id:
            conn.execute(
                sa.text("UPDATE materias SET categoria_plus_id = :cp_id WHERE id = :mid"),
                {'cp_id': cp_id, 'mid': mid},
            )

    # 3. Drop old categoria column
    op.drop_column('materias', 'categoria')


def downgrade() -> None:
    # Restore categoria column
    op.add_column('materias', sa.Column('categoria', sa.String(20), nullable=True))

    # Copy back string values via join
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "UPDATE materias m SET categoria = cp.codigo "
            "FROM categorias_plus cp "
            "WHERE m.categoria_plus_id = cp.id AND cp.deleted_at IS NULL"
        ),
    )

    op.drop_column('materias', 'categoria_plus_id')
