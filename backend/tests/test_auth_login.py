from datetime import datetime, timezone

import jwt as pyjwt
import pytest
import pytest_asyncio

from app.core.config import Settings
from app.core.security import hash_password
from app.models.tenant import Tenant
from app.models.user import User


@pytest_asyncio.fixture
async def tenant(db_session):
    t = Tenant(nombre='Test', codigo='TST')
    db_session.add(t)
    await db_session.flush()
    return t


@pytest_asyncio.fixture
async def active_user(db_session, tenant):
    u = User(
        email='docente@test.com',
        password_hash=hash_password('pass123'),
        tenant_id=tenant.id,
        is_active=True,
    )
    db_session.add(u)
    await db_session.flush()
    return u


@pytest_asyncio.fixture
async def inactive_user(db_session, tenant):
    u = User(
        email='inactivo@test.com',
        password_hash=hash_password('pass123'),
        tenant_id=tenant.id,
        is_active=False,
    )
    db_session.add(u)
    await db_session.flush()
    return u


@pytest_asyncio.fixture
async def deleted_user(db_session, tenant):
    u = User(
        email='deleted@test.com',
        password_hash=hash_password('pass123'),
        tenant_id=tenant.id,
        is_active=True,
        deleted_at=datetime.now(timezone.utc),
    )
    db_session.add(u)
    await db_session.flush()
    return u


class TestLogin:
    async def test_login_success_returns_tokens(self, async_client, active_user, tenant):
        response = await async_client.post(
            '/api/v1/auth/login',
            json={'email': 'docente@test.com', 'password': 'pass123'},
        )
        assert response.status_code == 200
        data = response.json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['token_type'] == 'bearer'
        assert 'expires_in' in data

    async def test_login_wrong_password_returns_401(self, async_client, active_user):
        response = await async_client.post(
            '/api/v1/auth/login',
            json={'email': 'docente@test.com', 'password': 'wrong_pass'},
        )
        assert response.status_code == 401
        assert 'Credenciales inválidas' in response.json()['detail']

    async def test_login_nonexistent_email_returns_401(self, async_client):
        response = await async_client.post(
            '/api/v1/auth/login',
            json={'email': 'noexiste@test.com', 'password': 'pass123'},
        )
        assert response.status_code == 401

    async def test_login_deleted_user_returns_401(self, async_client, deleted_user):
        response = await async_client.post(
            '/api/v1/auth/login',
            json={'email': 'deleted@test.com', 'password': 'pass123'},
        )
        assert response.status_code == 401

    async def test_login_inactive_user_returns_401(self, async_client, inactive_user):
        response = await async_client.post(
            '/api/v1/auth/login',
            json={'email': 'inactivo@test.com', 'password': 'pass123'},
        )
        assert response.status_code == 401

    async def test_login_jwt_has_correct_claims(self, async_client, active_user, tenant):
        response = await async_client.post(
            '/api/v1/auth/login',
            json={'email': 'docente@test.com', 'password': 'pass123'},
        )
        data = response.json()
        settings = Settings()
        payload = pyjwt.decode(
            data['access_token'], settings.secret_key, algorithms=['HS256'],
        )
        assert payload['sub'] == str(active_user.id)
        assert payload['tenant_id'] == str(tenant.id)
        assert payload['roles'] == []
        assert 'exp' in payload
        assert 'iat' in payload
        assert 'permissions' not in payload
        assert 'scope' not in payload
