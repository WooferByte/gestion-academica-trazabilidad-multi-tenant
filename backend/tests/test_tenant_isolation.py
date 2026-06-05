import pytest

from app.models.tenant import Tenant
from app.repositories.base import BaseRepository
from tests.helpers import TestModel


class TestModelRepo(BaseRepository[TestModel]):
    __model__ = TestModel


@pytest.fixture
async def setup_tenants(db_session):
    tenant_a = Tenant(nombre='Tenant A', codigo='TA-ISO')
    tenant_b = Tenant(nombre='Tenant B', codigo='TB-ISO')
    db_session.add(tenant_a)
    db_session.add(tenant_b)
    await db_session.flush()

    repo_a = TestModelRepo(session=db_session, tenant_id=tenant_a.id)
    repo_b = TestModelRepo(session=db_session, tenant_id=tenant_b.id)

    for i in range(5):
        await repo_a.create(nombre=f'A-{i}', codigo=f'TA{i:02d}')
        await repo_b.create(nombre=f'B-{i}', codigo=f'TB{i:02d}')

    return repo_a, repo_b, tenant_a, tenant_b


class TestTenantIsolation:
    @pytest.mark.asyncio
    async def test_get_isolation(self, setup_tenants, db_session):
        repo_a, repo_b, tenant_a, tenant_b = setup_tenants
        a_records = await repo_a.get_multi()
        b_records = await repo_b.get_multi()
        assert len(a_records) == 5
        assert len(b_records) == 5
        for a in a_records:
            assert a.tenant_id == tenant_a.id
        for b in b_records:
            assert b.tenant_id == tenant_b.id
        a_ids = {r.id for r in a_records}
        b_ids = {r.id for r in b_records}
        assert a_ids.isdisjoint(b_ids)

    @pytest.mark.asyncio
    async def test_get_multi_isolation(self, setup_tenants):
        repo_a, repo_b, tenant_a, tenant_b = setup_tenants
        a_all = await repo_a.get_multi()
        b_all = await repo_b.get_multi()
        for item in a_all:
            assert item.tenant_id == tenant_a.id
        for item in b_all:
            assert item.tenant_id == tenant_b.id

    @pytest.mark.asyncio
    async def test_exists_isolation(self, setup_tenants):
        repo_a, repo_b, tenant_a, tenant_b = setup_tenants
        a_records = await repo_a.get_multi()
        for record in a_records:
            assert await repo_a.exists(codigo=record.codigo) is True
            assert await repo_b.exists(codigo=record.codigo) is False

    @pytest.mark.asyncio
    async def test_update_isolation(self, setup_tenants):
        repo_a, repo_b, tenant_a, tenant_b = setup_tenants
        a_records = await repo_a.get_multi()
        target = a_records[0]
        updated = await repo_a.update(target, nombre='Updated A')
        assert updated.nombre == 'Updated A'
        target_b = await repo_b.get(target.id)
        assert target_b is None

    @pytest.mark.asyncio
    async def test_soft_delete_isolation(self, setup_tenants):
        repo_a, repo_b, tenant_a, tenant_b = setup_tenants
        a_records = await repo_a.get_multi()
        target = a_records[0]
        await repo_a.soft_delete(target)
        assert await repo_a.get(target.id) is None
        assert await repo_b.get(target.id) is None

    @pytest.mark.asyncio
    async def test_get_with_deleted_isolation(self, setup_tenants):
        repo_a, repo_b, tenant_a, tenant_b = setup_tenants
        a_records = await repo_a.get_multi()
        target = a_records[0]
        await repo_a.soft_delete(target)
        assert await repo_a.get_with_deleted(target.id) is not None
        assert await repo_b.get_with_deleted(target.id) is None
