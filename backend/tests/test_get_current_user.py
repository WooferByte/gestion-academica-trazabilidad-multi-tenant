from datetime import datetime, timedelta, timezone

import jwt as pyjwt
import pytest
import pytest_asyncio
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.core.dependencies import get_current_user, get_db
from app.core.security import create_access_token, hash_password
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.auth import UserContext


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


class TestGetCurrentUser:
    def _make_app(self):
        app = FastAPI()

        @app.get('/protected')
        async def protected(ctx: UserContext = Depends(get_current_user)):
            return {
                'user_id': str(ctx.user_id),
                'tenant_id': str(ctx.tenant_id),
                'roles': ctx.roles,
            }

        return app

    async def test_valid_token_returns_user_context(self, db_session, tenant, user):
        app = self._make_app()
        app.dependency_overrides[get_db] = lambda: db_session
        transport = ASGITransport(app=app)

        token = create_access_token(
            user_id=str(user.id),
            tenant_id=str(tenant.id),
            roles=['admin'],
        )

        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get(
                '/protected',
                headers={'Authorization': f'Bearer {token}'},
            )
        assert response.status_code == 200
        data = response.json()
        assert data['user_id'] == str(user.id)
        assert data['tenant_id'] == str(tenant.id)
        assert data['roles'] == ['admin']

    async def test_expired_token_returns_401(self, db_session, tenant, user):
        app = self._make_app()
        app.dependency_overrides[get_db] = lambda: db_session
        transport = ASGITransport(app=app)

        settings = Settings()
        payload = {
            'sub': str(user.id),
            'tenant_id': str(tenant.id),
            'roles': [],
            'exp': datetime.now(timezone.utc) - timedelta(hours=1),
            'iat': datetime.now(timezone.utc) - timedelta(hours=2),
        }
        expired_token = pyjwt.encode(payload, settings.secret_key, algorithm='HS256')

        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get(
                '/protected',
                headers={'Authorization': f'Bearer {expired_token}'},
            )
        assert response.status_code == 401

    async def test_invalid_signature_returns_401(self, db_session, tenant, user):
        app = self._make_app()
        app.dependency_overrides[get_db] = lambda: db_session
        transport = ASGITransport(app=app)

        payload = {
            'sub': str(user.id),
            'tenant_id': str(tenant.id),
            'roles': [],
            'exp': datetime.now(timezone.utc) + timedelta(hours=1),
            'iat': datetime.now(timezone.utc),
        }
        fake_token = pyjwt.encode(
            payload,
            'wrong-secret-key-that-is-at-least-32-chars-long!',
            algorithm='HS256',
        )

        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get(
                '/protected',
                headers={'Authorization': f'Bearer {fake_token}'},
            )
        assert response.status_code == 401

    async def test_token_without_tenant_id_returns_401(self, db_session, tenant, user):
        app = self._make_app()
        app.dependency_overrides[get_db] = lambda: db_session
        transport = ASGITransport(app=app)

        settings = Settings()
        payload = {
            'sub': str(user.id),
            'roles': [],
            'exp': datetime.now(timezone.utc) + timedelta(hours=1),
            'iat': datetime.now(timezone.utc),
        }
        bad_token = pyjwt.encode(payload, settings.secret_key, algorithm='HS256')

        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get(
                '/protected',
                headers={'Authorization': f'Bearer {bad_token}'},
            )
        assert response.status_code == 401

    async def test_valid_token_without_user_returns_401(self, db_session, tenant, user):
        """Token for a user that doesn't exist (deleted) should return 401."""
        app = self._make_app()
        app.dependency_overrides[get_db] = lambda: db_session
        transport = ASGITransport(app=app)

        fake_user_id = '00000000-0000-0000-0000-000000000000'
        token = create_access_token(
            user_id=fake_user_id,
            tenant_id=str(tenant.id),
            roles=[],
        )

        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get(
                '/protected',
                headers={'Authorization': f'Bearer {token}'},
            )
        assert response.status_code == 401

    async def test_2fa_token_rejected_by_get_current_user(self, db_session, tenant, user):
        """A 2fa_token should not work with get_current_user."""
        app = self._make_app()
        app.dependency_overrides[get_db] = lambda: db_session
        transport = ASGITransport(app=app)

        from app.core.security import create_2fa_token
        fa2_token = create_2fa_token(
            user_id=str(user.id),
            tenant_id=str(tenant.id),
        )

        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get(
                '/protected',
                headers={'Authorization': f'Bearer {fa2_token}'},
            )
        assert response.status_code == 401
