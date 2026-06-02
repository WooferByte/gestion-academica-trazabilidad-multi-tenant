import uuid

import pytest

from app.core.tenancy import TenantContext, get_tenant
from app.repositories.base import BaseRepository
from app.models.tenant import Tenant
from tests.helpers import TestModel


class TestTenancyLayer:
    async def test_tenant_context_holds_tenant_id(self):
        tenant_id = uuid.uuid4()
        context = TenantContext(tenant_id=tenant_id)
        assert context.tenant_id == tenant_id

    async def test_get_tenant_returns_context_with_correct_id(self):
        tenant_id = uuid.uuid4()
        context = await get_tenant(tenant_id=tenant_id)
        assert isinstance(context, TenantContext)
        assert context.tenant_id == tenant_id

    async def test_multiple_tenants_have_different_contexts(self):
        id_a = uuid.uuid4()
        id_b = uuid.uuid4()
        ctx_a = TenantContext(tenant_id=id_a)
        ctx_b = TenantContext(tenant_id=id_b)
        assert ctx_a.tenant_id == id_a
        assert ctx_b.tenant_id == id_b
        assert ctx_a.tenant_id != ctx_b.tenant_id

    async def test_tenant_context_is_immutable_like_object(self):
        tenant_id = uuid.uuid4()
        context = TenantContext(tenant_id=tenant_id)
        assert context.tenant_id == tenant_id

    async def test_tenant_context_can_be_used_in_repository(
        self, db_session
    ):
        tenant_a = Tenant(nombre='Tenant A', codigo='TA')
        db_session.add(tenant_a)
        await db_session.flush()

        class TestModelRepo(BaseRepository[TestModel]):
            __model__ = TestModel

        obj = TestModel(nombre='Test', codigo='T01', tenant_id=tenant_a.id)
        db_session.add(obj)
        await db_session.flush()

        repo = TestModelRepo(session=db_session, tenant_id=tenant_a.id)
        result = await repo.get(obj.id)
        assert result is not None
        assert result.id == obj.id
        assert result.tenant_id == tenant_a.id
