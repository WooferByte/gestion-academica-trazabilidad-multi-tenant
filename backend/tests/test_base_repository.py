import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import SoftDeletedException
from app.models.tenant import Tenant
from app.repositories.base import BaseRepository
from tests.helpers import TestModel


class TestModelRepo(BaseRepository[TestModel]):
    __model__ = TestModel


@pytest.fixture
async def tenant_a(db_session):
    t = Tenant(nombre='Tenant A', codigo='TA')
    db_session.add(t)
    await db_session.flush()
    return t


@pytest.fixture
async def tenant_b(db_session):
    t = Tenant(nombre='Tenant B', codigo='TB')
    db_session.add(t)
    await db_session.flush()
    return t


@pytest.fixture
async def repo_a(db_session, tenant_a):
    return TestModelRepo(session=db_session, tenant_id=tenant_a.id)


@pytest.fixture
async def repo_b(db_session, tenant_b):
    return TestModelRepo(session=db_session, tenant_id=tenant_b.id)


class TestBaseRepository:
    @pytest.mark.asyncio
    async def test_create_assigns_tenant_id(self, repo_a, tenant_a):
        obj = await repo_a.create(nombre='Create Test', codigo='CR01')
        assert obj.tenant_id == tenant_a.id
        assert obj.id is not None
        assert obj.nombre == 'Create Test'
        assert obj.codigo == 'CR01'

    @pytest.mark.asyncio
    async def test_get_filters_by_tenant(self, repo_a, repo_b, tenant_a, tenant_b):
        obj = await repo_a.create(nombre='Only A', codigo='OA01')

        result_a = await repo_a.get(obj.id)
        assert result_a is not None
        assert result_a.id == obj.id

        result_b = await repo_b.get(obj.id)
        assert result_b is None

    @pytest.mark.asyncio
    async def test_get_multi_pagination(self, repo_a):
        for i in range(25):
            await repo_a.create(nombre=f'Item {i}', codigo=f'IT{i:02d}')

        page1 = await repo_a.get_multi(skip=0, limit=10)
        assert len(page1) == 10

        page2 = await repo_a.get_multi(skip=10, limit=10)
        assert len(page2) == 10

        page3 = await repo_a.get_multi(skip=20, limit=10)
        assert len(page3) == 5

        ids_page1 = {o.id for o in page1}
        ids_page2 = {o.id for o in page2}
        assert ids_page1.isdisjoint(ids_page2)

    @pytest.mark.asyncio
    async def test_get_multi_only_returns_tenant_records(self, repo_a, repo_b):
        await repo_a.create(nombre='A1', codigo='A01')
        await repo_a.create(nombre='A2', codigo='A02')
        await repo_b.create(nombre='B1', codigo='B01')

        results_a = await repo_a.get_multi()
        assert len(results_a) == 2

        results_b = await repo_b.get_multi()
        assert len(results_b) == 1

    @pytest.mark.asyncio
    async def test_update_partial_merge(self, repo_a):
        obj = await repo_a.create(nombre='Original', codigo='ORIG')
        updated = await repo_a.update(obj, nombre='Modified')
        assert updated.nombre == 'Modified'
        assert updated.codigo == 'ORIG'

    @pytest.mark.asyncio
    async def test_exists_within_tenant(self, repo_a, repo_b):
        await repo_a.create(nombre='Exist Test', codigo='E01')

        assert await repo_a.exists(codigo='E01') is True
        assert await repo_b.exists(codigo='E01') is False

    @pytest.mark.asyncio
    async def test_exists_returns_false_for_nonexistent(self, repo_a):
        assert await repo_a.exists(codigo='DOES_NOT_EXIST') is False

    @pytest.mark.asyncio
    async def test_create_multiple_records(self, repo_a):
        o1 = await repo_a.create(nombre='Multi1', codigo='M01')
        o2 = await repo_a.create(nombre='Multi2', codigo='M02')
        assert o1.id != o2.id
        assert o1.tenant_id == o2.tenant_id


class TestSoftDelete:
    @pytest.mark.asyncio
    async def test_soft_delete_sets_deleted_at(self, repo_a):
        obj = await repo_a.create(nombre='To Delete', codigo='DEL01')
        assert obj.deleted_at is None

        deleted = await repo_a.soft_delete(obj)
        assert deleted.deleted_at is not None

    @pytest.mark.asyncio
    async def test_get_excludes_soft_deleted(self, repo_a):
        obj = await repo_a.create(nombre='Will Delete', codigo='WD01')
        await repo_a.soft_delete(obj)
        result = await repo_a.get(obj.id)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_multi_excludes_soft_deleted(self, repo_a):
        obj = await repo_a.create(nombre='Keep Me', codigo='KP01')
        for i in range(3):
            o = await repo_a.create(nombre=f'Del Me {i}', codigo=f'DM{i:02d}')
            await repo_a.soft_delete(o)

        remaining = await repo_a.get_multi()
        assert len(remaining) == 1
        assert remaining[0].id == obj.id

    @pytest.mark.asyncio
    async def test_get_with_deleted_includes_soft_deleted(self, repo_a):
        obj = await repo_a.create(nombre='Soft Deleted', codigo='SD01')
        await repo_a.soft_delete(obj)

        result = await repo_a.get_with_deleted(obj.id)
        assert result is not None
        assert result.id == obj.id
        assert result.deleted_at is not None

    @pytest.mark.asyncio
    async def test_update_on_soft_deleted_raises_exception(self, repo_a):
        obj = await repo_a.create(nombre='Gonna Delete', codigo='GD01')
        await repo_a.soft_delete(obj)

        with pytest.raises(SoftDeletedException):
            await repo_a.update(obj, nombre='Should Fail')

    @pytest.mark.asyncio
    async def test_exists_excludes_soft_deleted(self, repo_a):
        obj = await repo_a.create(nombre='Exists Test', codigo='EX01')
        await repo_a.soft_delete(obj)
        assert await repo_a.exists(codigo='EX01') is False

    @pytest.mark.asyncio
    async def test_get_with_deleted_still_filters_by_tenant(self, repo_a, repo_b):
        obj_a = await repo_a.create(nombre='Tenant A', codigo='TA01')
        obj_b = await repo_b.create(nombre='Tenant B', codigo='TB01')
        await repo_a.soft_delete(obj_a)

        result_a = await repo_a.get_with_deleted(obj_a.id)
        assert result_a is not None

        result_b = await repo_b.get_with_deleted(obj_a.id)
        assert result_b is None
