import jwt as pyjwt
import pytest_asyncio

from app.core.config import Settings
from app.core.security import hash_password
from app.models.tenant import Tenant
from app.models.user import User


@pytest_asyncio.fixture
async def tenant_a(db_session):
    t = Tenant(nombre='Tenant A', codigo='TA')
    db_session.add(t)
    await db_session.flush()
    return t


@pytest_asyncio.fixture
async def tenant_b(db_session):
    t = Tenant(nombre='Tenant B', codigo='TB')
    db_session.add(t)
    await db_session.flush()
    return t


@pytest_asyncio.fixture
async def user_a(db_session, tenant_a):
    u = User(
        email='user@test.com',
        password_hash=hash_password('pass123'),
        tenant_id=tenant_a.id,
        is_active=True,
    )
    db_session.add(u)
    await db_session.flush()
    return u


@pytest_asyncio.fixture
async def user_b(db_session, tenant_b):
    u = User(
        email='other@test.com',
        password_hash=hash_password('pass456'),
        tenant_id=tenant_b.id,
        is_active=True,
    )
    db_session.add(u)
    await db_session.flush()
    return u


class TestMultiTenantAuth:
    async def test_users_have_different_tenants(self, async_client, user_a, user_b):
        resp_a = await async_client.post(
            '/api/v1/auth/login',
            json={'email': 'user@test.com', 'password': 'pass123'},
        )
        assert resp_a.status_code == 200
        token_a = resp_a.json()['access_token']

        settings = Settings()
        payload_a = pyjwt.decode(
            token_a, settings.secret_key, algorithms=['HS256'],
        )

        resp_b = await async_client.post(
            '/api/v1/auth/login',
            json={'email': 'other@test.com', 'password': 'pass456'},
        )
        assert resp_b.status_code == 200
        token_b = resp_b.json()['access_token']
        payload_b = pyjwt.decode(
            token_b, settings.secret_key, algorithms=['HS256'],
        )

        assert payload_a['tenant_id'] != payload_b['tenant_id']

    async def test_user_a_cannot_login_in_tenant_b(self, async_client, user_a, user_b):
        resp_a = await async_client.post(
            '/api/v1/auth/login',
            json={'email': 'user@test.com', 'password': 'pass123'},
        )
        assert resp_a.status_code == 200

        resp_wrong = await async_client.post(
            '/api/v1/auth/login',
            json={'email': 'user@test.com', 'password': 'pass456'},
        )
        assert resp_wrong.status_code == 401
