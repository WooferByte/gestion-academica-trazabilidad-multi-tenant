import pyotp
import pytest_asyncio

from app.core.security import encrypt, hash_password
from app.models.tenant import Tenant
from app.models.user import User
from app.repositories.user_repository import UserRepository
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


@pytest_asyncio.fixture
async def user_with_2fa(db_session, tenant):
    secret = pyotp.random_base32()
    u = User(
        email='2fa@test.com',
        password_hash=hash_password('pass123'),
        tenant_id=tenant.id,
        is_active=True,
        totp_secret_cifrado=encrypt(secret),
    )
    db_session.add(u)
    await db_session.flush()
    return u, secret


class Test2FAEnroll:
    async def _login_and_get_token(self, async_client):
        resp = await async_client.post(
            '/api/v1/auth/login',
            json={'email': 'user@test.com', 'password': 'pass123'},
        )
        return resp.json()['access_token']

    @pytest.mark.asyncio
    async def test_enroll_returns_secret_and_uri(self, async_client, user, tenant):
        token = await self._login_and_get_token(async_client)

        response = await async_client.post(
            '/api/v1/auth/2fa/enroll',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == 200
        data = response.json()
        assert 'secret' in data
        assert 'uri' in data
        assert data['uri'].startswith('otpauth://')

    @pytest.mark.asyncio
    async def test_reenroll_returns_conflict(self, async_client, user, db_session, tenant):
        token = await self._login_and_get_token(async_client)

        secret = pyotp.random_base32()
        repo = UserRepository(db_session, tenant.id)
        u = await repo.get(user.id)
        u.totp_secret_cifrado = encrypt(secret)
        await db_session.flush()

        response = await async_client.post(
            '/api/v1/auth/2fa/enroll',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == 409


class Test2FAVerify:
    async def _login_and_get_token(self, async_client):
        resp = await async_client.post(
            '/api/v1/auth/login',
            json={'email': 'user@test.com', 'password': 'pass123'},
        )
        return resp.json()['access_token']

    @pytest.mark.asyncio
    async def test_verify_with_valid_code_activates_2fa(self, async_client, user, tenant):
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        code = totp.now()
        token = await self._login_and_get_token(async_client)

        response = await async_client.post(
            '/api/v1/auth/2fa/verify',
            headers={'Authorization': f'Bearer {token}'},
            json={'secret': secret, 'code': code},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_verify_with_invalid_code_returns_400(self, async_client, user, tenant):
        token = await self._login_and_get_token(async_client)

        response = await async_client.post(
            '/api/v1/auth/2fa/verify',
            headers={'Authorization': f'Bearer {token}'},
            json={'secret': pyotp.random_base32(), 'code': '000000'},
        )
        assert response.status_code == 400


class Test2FALoginGate:
    @pytest.mark.asyncio
    async def test_login_requires_2fa_when_active(self, async_client, user_with_2fa):
        user, secret = user_with_2fa
        response = await async_client.post(
            '/api/v1/auth/login',
            json={'email': '2fa@test.com', 'password': 'pass123'},
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('2fa_required') is True
        assert '2fa_token' in data
        assert 'access_token' not in data

    @pytest.mark.asyncio
    async def test_validate_2fa_with_valid_code_emits_session(self, async_client, user_with_2fa):
        user, secret = user_with_2fa

        login_resp = await async_client.post(
            '/api/v1/auth/login',
            json={'email': '2fa@test.com', 'password': 'pass123'},
        )
        fa2_token = login_resp.json()['2fa_token']

        totp = pyotp.TOTP(secret)
        code = totp.now()

        validate_resp = await async_client.post(
            '/api/v1/auth/2fa/validate',
            json={'2fa_token': fa2_token, 'code': code},
        )
        assert validate_resp.status_code == 200
        data = validate_resp.json()
        assert 'access_token' in data
        assert 'refresh_token' in data

    @pytest.mark.asyncio
    async def test_validate_2fa_with_invalid_code_returns_401(self, async_client, user_with_2fa):
        user, secret = user_with_2fa

        login_resp = await async_client.post(
            '/api/v1/auth/login',
            json={'email': '2fa@test.com', 'password': 'pass123'},
        )
        fa2_token = login_resp.json()['2fa_token']

        validate_resp = await async_client.post(
            '/api/v1/auth/2fa/validate',
            json={'2fa_token': fa2_token, 'code': '000000'},
        )
        assert validate_resp.status_code == 401

    @pytest.mark.asyncio
    async def test_2fa_token_does_not_access_other_endpoints(self, async_client, user_with_2fa):
        user, secret = user_with_2fa

        login_resp = await async_client.post(
            '/api/v1/auth/login',
            json={'email': '2fa@test.com', 'password': 'pass123'},
        )
        fa2_token = login_resp.json()['2fa_token']

        response = await async_client.post(
            '/api/v1/auth/logout',
            headers={'Authorization': f'Bearer {fa2_token}'},
            json={'refresh_token': 'dummy'},
        )
        assert validate_resp.status_code == 200
        data = validate_resp.json()
        assert 'access_token' in data
        assert 'refresh_token' in data

    @pytest.mark.asyncio
    async def test_validate_2fa_with_invalid_code_returns_401(self, async_client, user_with_2fa):
        user, secret = user_with_2fa

        login_resp = await async_client.post(
            '/api/v1/auth/login',
            json={'email': '2fa@test.com', 'password': 'pass123'},
        )
        fa2_token = login_resp.json()['2fa_token']

        validate_resp = await async_client.post(
            '/api/v1/auth/2fa/validate',
            json={'2fa_token': fa2_token, 'code': code},
        )
        assert validate_resp.status_code == 200
        data = validate_resp.json()
        assert 'access_token' in data
        assert 'refresh_token' in data

    @pytest.mark.asyncio
    async def test_validate_2fa_with_invalid_code_returns_401(self, async_client, user_with_2fa):
        user, secret = user_with_2fa

        login_resp = await async_client.post(
            '/api/v1/auth/login',
            json={'email': '2fa@test.com', 'password': 'pass123'},
        )
        fa2_token = login_resp.json()['2fa_token']

        validate_resp = await async_client.post(
            '/api/v1/auth/2fa/validate',
            json={'2fa_token': fa2_token, 'code': '000000'},
        )
        assert validate_resp.status_code == 401

    @pytest.mark.asyncio
    async def test_2fa_token_does_not_access_other_endpoints(self, async_client, user_with_2fa):
        user, secret = user_with_2fa

        login_resp = await async_client.post(
            '/api/v1/auth/login',
            json={'email': '2fa@test.com', 'password': 'pass123'},
        )
        fa2_token = login_resp.json()['2fa_token']

        response = await async_client.post(
            '/api/v1/auth/logout',
            headers={'Authorization': f'Bearer {fa2_token}'},
            json={'refresh_token': 'dummy'},
        )
        assert response.status_code == 401
