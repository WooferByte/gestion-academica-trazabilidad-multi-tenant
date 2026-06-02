import hashlib
import os
from datetime import datetime, timedelta, timezone

import pytest_asyncio

from app.core.security import hash_password, verify_password
from app.models.tenant import Tenant
from app.models.user import PasswordResetToken, User


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


class TestForgotPassword:
    async def test_forgot_returns_token_in_debug_mode(self, async_client, user):
        os.environ['DEBUG'] = 'true'

        from app.core.config import Settings
        s = Settings()

        response = await async_client.post(
            '/api/v1/auth/forgot',
            json={'email': 'user@test.com'},
        )
        assert response.status_code == 200
        data = response.json()
        if s.debug:
            assert 'token' in data
            assert data['token'] is not None
            assert data['detail'] == 'Si el email existe, recibirás un enlace de recuperación'

    async def test_forgot_nonexistent_email_still_returns_200(self, async_client):
        response = await async_client.post(
            '/api/v1/auth/forgot',
            json={'email': 'noexiste@test.com'},
        )
        assert response.status_code == 200

    async def test_forgot_same_response_for_existing_and_nonexistent(self, async_client, user):
        r1 = await async_client.post(
            '/api/v1/auth/forgot',
            json={'email': 'user@test.com'},
        )
        r2 = await async_client.post(
            '/api/v1/auth/forgot',
            json={'email': 'noexiste@test.com'},
        )
        assert r1.status_code == 200
        assert r2.status_code == 200

    async def test_forgot_debug_false_does_not_expose_token(self, async_client, user):
        os.environ['DEBUG'] = 'false'

        response = await async_client.post(
            '/api/v1/auth/forgot',
            json={'email': 'user@test.com'},
        )
        assert response.status_code == 200
        data = response.json()
        assert 'token' not in data or data['token'] is None


class TestResetPassword:
    async def test_reset_with_valid_token_updates_password(self, async_client, user, db_session, tenant):
        token_value = 'valid-reset-token'
        token_hash = hashlib.sha256(token_value.encode('utf-8')).hexdigest()

        prt = PasswordResetToken(
            token_hash=token_hash,
            user_id=user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            tenant_id=tenant.id,
        )
        db_session.add(prt)
        await db_session.flush()

        response = await async_client.post(
            '/api/v1/auth/reset',
            json={'token': token_value, 'new_password': 'new_pass_123'},
        )
        assert response.status_code == 200

        await db_session.refresh(user)
        assert verify_password('new_pass_123', user.password_hash) is True

    async def test_reset_marks_token_as_used(self, async_client, user, db_session, tenant):
        token_value = 'single-use-token'
        token_hash = hashlib.sha256(token_value.encode('utf-8')).hexdigest()

        prt = PasswordResetToken(
            token_hash=token_hash,
            user_id=user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            tenant_id=tenant.id,
        )
        db_session.add(prt)
        await db_session.flush()

        response = await async_client.post(
            '/api/v1/auth/reset',
            json={'token': token_value, 'new_password': 'new_pass_123'},
        )
        assert response.status_code == 200

        await db_session.refresh(prt)
        assert prt.used_at is not None

    async def test_reset_with_expired_token_returns_401(self, async_client, user, db_session, tenant):
        token_value = 'expired-reset-token'
        token_hash = hashlib.sha256(token_value.encode('utf-8')).hexdigest()

        prt = PasswordResetToken(
            token_hash=token_hash,
            user_id=user.id,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
            tenant_id=tenant.id,
        )
        db_session.add(prt)
        await db_session.flush()

        response = await async_client.post(
            '/api/v1/auth/reset',
            json={'token': token_value, 'new_password': 'new_pass_123'},
        )
        assert response.status_code == 401

    async def test_reset_with_used_token_returns_401(self, async_client, user, db_session, tenant):
        token_value = 'used-token'
        token_hash = hashlib.sha256(token_value.encode('utf-8')).hexdigest()

        prt = PasswordResetToken(
            token_hash=token_hash,
            user_id=user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            tenant_id=tenant.id,
            used_at=datetime.now(timezone.utc),
        )
        db_session.add(prt)
        await db_session.flush()

        response = await async_client.post(
            '/api/v1/auth/reset',
            json={'token': token_value, 'new_password': 'new_pass_123'},
        )
        assert response.status_code == 401

    async def test_token_is_single_use(self, async_client, user, db_session, tenant):
        token_value = 'single-use-2'
        token_hash = hashlib.sha256(token_value.encode('utf-8')).hexdigest()

        prt = PasswordResetToken(
            token_hash=token_hash,
            user_id=user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            tenant_id=tenant.id,
        )
        db_session.add(prt)
        await db_session.flush()

        r1 = await async_client.post(
            '/api/v1/auth/reset',
            json={'token': token_value, 'new_password': 'new_pass_123'},
        )
        assert r1.status_code == 200

        r2 = await async_client.post(
            '/api/v1/auth/reset',
            json={'token': token_value, 'new_password': 'another_pass_456'},
        )
        assert r2.status_code == 401
