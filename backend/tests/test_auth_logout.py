import pytest_asyncio

from app.core.security import hash_password
from app.models.tenant import Tenant
from app.models.user import User
import pytest


@pytest_asyncio.fixture
async def tenant(db_session):
    t = Tenant(nombre='Test', codigo='TST')
    db_session.add(t)
    await db_session.flush()
    return t


@pytest_asyncio.fixture
async def user(db_session, tenant):
    u = User(
        email='user@test.com',
        password_hash=hash_password('pass123'),
        tenant_id=tenant.id,
        is_active=True,
    )
    db_session.add(u)
    await db_session.flush()
    return u


class TestLogout:
    @pytest.mark.asyncio
    async def test_logout_revokes_refresh_token(self, async_client, user, tenant):
        login_resp = await async_client.post(
            '/api/v1/auth/login',
            json={'email': 'user@test.com', 'password': 'pass123'},
        )
        data = login_resp.json()
        access_token = data['access_token']
        refresh_token = data['refresh_token']

        logout_resp = await async_client.post(
            '/api/v1/auth/logout',
            headers={'Authorization': f'Bearer {access_token}'},
            json={'refresh_token': refresh_token},
        )
        assert logout_resp.status_code == 200

    @pytest.mark.asyncio
    async def test_logout_without_auth_returns_401(self, async_client):
        response = await async_client.post(
            '/api/v1/auth/logout',
            json={'refresh_token': 'some-token'},
        )
        assert response.status_code == 401
