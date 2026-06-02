import hashlib
from datetime import datetime, timedelta, timezone

import pytest_asyncio

from app.core.security import hash_password
from app.models.tenant import Tenant
from app.models.user import RefreshToken, User


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


class TestRefresh:
    async def test_refresh_success_returns_new_tokens(self, async_client, user, tenant):
        login_resp = await async_client.post(
            '/api/v1/auth/login',
            json={'email': 'user@test.com', 'password': 'pass123'},
        )
        tokens = login_resp.json()

        response = await async_client.post(
            '/api/v1/auth/refresh',
            json={'refresh_token': tokens['refresh_token']},
        )
        assert response.status_code == 200
        data = response.json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['token_type'] == 'bearer'

    async def test_old_token_revoked_after_refresh(self, async_client, user, tenant):
        login_resp = await async_client.post(
            '/api/v1/auth/login',
            json={'email': 'user@test.com', 'password': 'pass123'},
        )
        tokens = login_resp.json()
        old_refresh = tokens['refresh_token']

        resp1 = await async_client.post(
            '/api/v1/auth/refresh',
            json={'refresh_token': old_refresh},
        )
        assert resp1.status_code == 200

        resp2 = await async_client.post(
            '/api/v1/auth/refresh',
            json={'refresh_token': old_refresh},
        )
        assert resp2.status_code == 401

    async def test_reuse_of_revoked_token_invalidates_family(self, async_client, user, tenant):
        login_resp = await async_client.post(
            '/api/v1/auth/login',
            json={'email': 'user@test.com', 'password': 'pass123'},
        )
        first_refresh = login_resp.json()['refresh_token']

        resp1 = await async_client.post(
            '/api/v1/auth/refresh',
            json={'refresh_token': first_refresh},
        )
        assert resp1.status_code == 200
        new_tokens = resp1.json()

        resp2 = await async_client.post(
            '/api/v1/auth/refresh',
            json={'refresh_token': first_refresh},
        )
        assert resp2.status_code == 401

        resp3 = await async_client.post(
            '/api/v1/auth/refresh',
            json={'refresh_token': new_tokens['refresh_token']},
        )
        assert resp3.status_code == 401

    async def test_refresh_with_expired_token_returns_401(self, async_client, user, tenant, db_session):
        token_hash = hashlib.sha256('expired-token'.encode('utf-8')).hexdigest()
        rt = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            family_id=user.id,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
            tenant_id=tenant.id,
        )
        db_session.add(rt)
        await db_session.flush()

        response = await async_client.post(
            '/api/v1/auth/refresh',
            json={'refresh_token': 'expired-token'},
        )
        assert response.status_code == 401
