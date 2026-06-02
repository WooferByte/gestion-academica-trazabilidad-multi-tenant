import pytest

from app.core.security import hash_password
from app.models.tenant import Tenant
from app.repositories.user_repository import UserRepository


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
    return UserRepository(session=db_session, tenant_id=tenant_a.id)


@pytest.fixture
async def repo_b(db_session, tenant_b):
    return UserRepository(session=db_session, tenant_id=tenant_b.id)


class TestUserRepository:
    async def test_get_by_email_finds_user(self, repo_a):
        await repo_a.create(
            email='findme@test.com',
            password_hash=hash_password('pass123'),
        )
        user = await repo_a.get_by_email('findme@test.com')
        assert user is not None
        assert user.email == 'findme@test.com'

    async def test_get_by_email_returns_none_if_not_found(self, repo_a):
        user = await repo_a.get_by_email('noexiste@test.com')
        assert user is None

    async def test_create_assigns_tenant_id(self, repo_a, tenant_a):
        user = await repo_a.create(
            email='new@test.com',
            password_hash=hash_password('pass123'),
        )
        assert user.tenant_id == tenant_a.id

    async def test_get_by_email_respects_tenant_scope(self, repo_a, repo_b):
        await repo_a.create(
            email='shared@test.com',
            password_hash=hash_password('pass123'),
        )
        found_a = await repo_a.get_by_email('shared@test.com')
        assert found_a is not None

        found_b = await repo_b.get_by_email('shared@test.com')
        assert found_b is None

    async def test_get_by_email_excludes_soft_deleted(self, repo_a):
        user = await repo_a.create(
            email='todelete@test.com',
            password_hash=hash_password('pass123'),
        )
        await repo_a.soft_delete(user)

        found = await repo_a.get_by_email('todelete@test.com')
        assert found is None
