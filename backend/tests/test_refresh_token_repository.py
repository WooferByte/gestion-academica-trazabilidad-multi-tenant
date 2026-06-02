import hashlib
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.core.security import hash_password
from app.models.tenant import Tenant
from app.models.user import RefreshToken, User
from app.repositories.refresh_token_repository import RefreshTokenRepository


@pytest.fixture
async def tenant(db_session):
    t = Tenant(nombre='Test', codigo='TST')
    db_session.add(t)
    await db_session.flush()
    return t


@pytest.fixture
async def user(db_session, tenant):
    u = User(
        email='user@test.com',
        password_hash=hash_password('pass123'),
        tenant_id=tenant.id,
    )
    db_session.add(u)
    await db_session.flush()
    return u


@pytest.fixture
async def repo(db_session, tenant):
    return RefreshTokenRepository(session=db_session, tenant_id=tenant.id)


class TestRefreshTokenRepository:
    async def test_create_token_persists_correctly(self, repo, user):
        token_value = str(uuid.uuid4())
        token_hash = hashlib.sha256(token_value.encode('utf-8')).hexdigest()
        family_id = uuid.uuid4()
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)

        rt = await repo.create_token(
            user_id=user.id,
            token_hash=token_hash,
            family_id=family_id,
            expires_at=expires_at,
        )
        assert rt.id is not None
        assert rt.token_hash == token_hash
        assert rt.family_id == family_id
        assert rt.expires_at is not None
        assert rt.revoked_at is None

    async def test_get_by_token_hash_finds_token(self, repo, user):
        token_value = str(uuid.uuid4())
        token_hash = hashlib.sha256(token_value.encode('utf-8')).hexdigest()
        family_id = uuid.uuid4()
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)

        await repo.create_token(
            user_id=user.id,
            token_hash=token_hash,
            family_id=family_id,
            expires_at=expires_at,
        )

        found = await repo.get_by_token_hash(token_hash)
        assert found is not None
        assert found.token_hash == token_hash

    async def test_revoke_sets_revoked_at(self, repo, user):
        token_value = str(uuid.uuid4())
        token_hash = hashlib.sha256(token_value.encode('utf-8')).hexdigest()
        family_id = uuid.uuid4()
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)

        rt = await repo.create_token(
            user_id=user.id,
            token_hash=token_hash,
            family_id=family_id,
            expires_at=expires_at,
        )
        assert rt.revoked_at is None

        await repo.revoke(rt)
        assert rt.revoked_at is not None

    async def test_revoke_family_revokes_all_tokens(self, repo, user):
        family_id = uuid.uuid4()
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)

        rt1 = await repo.create_token(
            user_id=user.id,
            token_hash=hashlib.sha256(b't1').hexdigest(),
            family_id=family_id,
            expires_at=expires_at,
        )
        rt2 = await repo.create_token(
            user_id=user.id,
            token_hash=hashlib.sha256(b't2').hexdigest(),
            family_id=family_id,
            expires_at=expires_at,
        )

        await repo.revoke_family(family_id)

        f1 = await repo.get_by_token_hash(hashlib.sha256(b't1').hexdigest())
        f2 = await repo.get_by_token_hash(hashlib.sha256(b't2').hexdigest())
        assert f1.revoked_at is not None
        assert f2.revoked_at is not None

    async def test_token_hash_is_sha256_of_uuid(self, repo, user):
        token_value = str(uuid.uuid4())
        expected_hash = hashlib.sha256(token_value.encode('utf-8')).hexdigest()
        family_id = uuid.uuid4()
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)

        rt = await repo.create_token(
            user_id=user.id,
            token_hash=expected_hash,
            family_id=family_id,
            expires_at=expires_at,
        )
        assert rt.token_hash == expected_hash
        assert rt.token_hash != token_value

    async def test_revoke_all_for_user(self, repo, user):
        family_id_a = uuid.uuid4()
        family_id_b = uuid.uuid4()
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)

        await repo.create_token(
            user_id=user.id,
            token_hash=hashlib.sha256(b'u1').hexdigest(),
            family_id=family_id_a,
            expires_at=expires_at,
        )
        await repo.create_token(
            user_id=user.id,
            token_hash=hashlib.sha256(b'u2').hexdigest(),
            family_id=family_id_b,
            expires_at=expires_at,
        )

        await repo.revoke_all_for_user(user.id)

        f1 = await repo.get_by_token_hash(hashlib.sha256(b'u1').hexdigest())
        f2 = await repo.get_by_token_hash(hashlib.sha256(b'u2').hexdigest())
        assert f1.revoked_at is not None
        assert f2.revoked_at is not None
