import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.tenant import Tenant
from tests.helpers import TestModel


class TestBaseModelMixin:
    @pytest.mark.asyncio
    async def test_model_has_auto_uuid(self, db_session):
        tenant = Tenant(nombre='Tenant', codigo='TNT0')
        db_session.add(tenant)
        await db_session.flush()

        tm = TestModel(nombre='Test', codigo='T01', tenant_id=tenant.id)
        db_session.add(tm)
        await db_session.flush()

        assert tm.id is not None
        assert isinstance(tm.id, uuid.UUID)

    @pytest.mark.asyncio
    async def test_model_has_tenant_id(self, db_session):
        tenant = Tenant(nombre='Tenant', codigo='TNT')
        db_session.add(tenant)
        await db_session.flush()

        tm = TestModel(nombre='Test', codigo='T01', tenant_id=tenant.id)
        db_session.add(tm)
        await db_session.flush()

        assert tm.tenant_id == tenant.id

    @pytest.mark.asyncio
    async def test_model_fk_violation_on_invalid_tenant(self, db_session):
        fake_id = uuid.uuid4()
        tm = TestModel(nombre='Test', codigo='FKFAIL', tenant_id=fake_id)
        db_session.add(tm)
        with pytest.raises(IntegrityError):
            await db_session.flush()

    @pytest.mark.asyncio
    async def test_created_at_set_on_create(self, db_session):
        tenant = Tenant(nombre='Tenant', codigo='TNT2')
        db_session.add(tenant)
        await db_session.flush()

        tm = TestModel(nombre='Test', codigo='T02', tenant_id=tenant.id)
        db_session.add(tm)
        await db_session.flush()

        assert tm.created_at is not None
        assert tm.created_at.tzinfo is not None

    @pytest.mark.asyncio
    async def test_updated_at_has_value(self, db_session):
        tenant = Tenant(nombre='Tenant', codigo='TNT3')
        db_session.add(tenant)
        await db_session.flush()

        tm = TestModel(nombre='Original', codigo='T03', tenant_id=tenant.id)
        db_session.add(tm)
        await db_session.flush()

        assert tm.updated_at is not None
        assert tm.updated_at.tzinfo is not None

    @pytest.mark.asyncio
    async def test_deleted_at_is_nullable(self, db_session):
        tenant = Tenant(nombre='Tenant', codigo='TNT4')
        db_session.add(tenant)
        await db_session.flush()

        tm = TestModel(nombre='Test', codigo='T04', tenant_id=tenant.id)
        db_session.add(tm)
        await db_session.flush()

        assert tm.deleted_at is None

    @pytest.mark.asyncio
    async def test_tenant_has_nullable_tenant_id(self, db_session):
        tenant = Tenant(nombre='Root', codigo='ROOT')
        db_session.add(tenant)
        await db_session.flush()

        assert tenant.tenant_id is None
