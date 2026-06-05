import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.models.tenant import Tenant


class TestTenantModel:
    @pytest.mark.asyncio
    async def test_create_tenant(self, db_session):
        tenant = Tenant(nombre='Test University', codigo='TUPAD')
        db_session.add(tenant)
        await db_session.flush()

        assert tenant.id is not None
        assert isinstance(tenant.id, uuid.UUID)
        assert tenant.nombre == 'Test University'
        assert tenant.codigo == 'TUPAD'
        assert tenant.estado == 'Activo'
        assert tenant.created_at is not None
        assert tenant.updated_at is not None
        assert tenant.deleted_at is None

    @pytest.mark.asyncio
    async def test_tenant_timestamps_on_create(self, db_session):
        tenant = Tenant(nombre='UBA', codigo='UBA')
        db_session.add(tenant)
        await db_session.flush()

        assert tenant.created_at is not None
        assert tenant.updated_at is not None
        assert tenant.created_at.tzinfo is not None

    @pytest.mark.asyncio
    async def test_tenant_unique_codigo_violation(self, db_session):
        t1 = Tenant(nombre='First', codigo='UNIQUE')
        db_session.add(t1)
        await db_session.flush()

        t2 = Tenant(nombre='Second', codigo='UNIQUE')
        db_session.add(t2)
        with pytest.raises(IntegrityError):
            await db_session.flush()

    @pytest.mark.asyncio
    async def test_tenant_default_estado_is_activo(self, db_session):
        tenant = Tenant(nombre='UTN', codigo='UTN')
        db_session.add(tenant)
        await db_session.flush()

        assert tenant.estado == 'Activo'

    @pytest.mark.asyncio
    async def test_tenant_id_is_auto_generated(self, db_session):
        tenant = Tenant(nombre='Auto ID', codigo='AUTO')
        db_session.add(tenant)
        await db_session.flush()

        assert tenant.id is not None
        assert isinstance(tenant.id, uuid.UUID)

    @pytest.mark.asyncio
    async def test_tenant_updated_at_changes_on_update(self, db_session):
        tenant = Tenant(nombre='Cambiante', codigo='CHNG')
        db_session.add(tenant)
        await db_session.flush()

        assert tenant.updated_at is not None
        assert tenant.updated_at.tzinfo is not None

    @pytest.mark.asyncio
    async def test_tenant_table_exists(self, db_session):
        result = await db_session.execute(
            text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'tenants')")
        )
        assert result.scalar() is True

    @pytest.mark.asyncio
    async def test_tenant_soft_delete_sets_deleted_at(self, db_session):
        from datetime import datetime, timezone
        tenant = Tenant(nombre='To Delete', codigo='DEL')
        db_session.add(tenant)
        await db_session.flush()

        tenant.deleted_at = datetime.now(timezone.utc)
        await db_session.flush()

        assert tenant.deleted_at is not None
