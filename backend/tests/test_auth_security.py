import os
from datetime import datetime, timedelta, timezone

import jwt as pyjwt
import pytest

from app.core.config import Settings
from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_begins_with_argon2id(self):
        hashed = hash_password('mi_password')
        assert hashed.startswith('$argon2id$')

    def test_hash_is_not_input(self):
        password = 'mi_password'
        hashed = hash_password(password)
        assert hashed != password

    def test_verify_correct_password(self):
        hashed = hash_password('mi_pass')
        assert verify_password('mi_pass', hashed) is True

    def test_verify_incorrect_password(self):
        hashed = hash_password('mi_pass')
        assert verify_password('wrong_pass', hashed) is False

    def test_same_password_different_hashes(self):
        h1 = hash_password('password')
        h2 = hash_password('password')
        assert h1 != h2


class TestJWTTokens:
    def test_create_access_token_emits_decodable_token(self):
        token = create_access_token(
            user_id='usr-123', tenant_id='tnt-456', roles=['admin'],
        )
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_valid_token(self):
        token = create_access_token(
            user_id='usr-123', tenant_id='tnt-456', roles=['admin'],
        )
        payload = decode_token(token)
        assert payload['sub'] == 'usr-123'
        assert payload['tenant_id'] == 'tnt-456'
        assert payload['roles'] == ['admin']

    def test_token_has_minimal_claims(self):
        token = create_access_token(
            user_id='usr-123', tenant_id='tnt-456', roles=['admin'],
        )
        payload = decode_token(token)
        assert 'sub' in payload
        assert 'tenant_id' in payload
        assert 'roles' in payload
        assert 'exp' in payload
        assert 'iat' in payload
        assert 'permissions' not in payload
        assert 'scope' not in payload

    def test_expired_token_raises_error(self):
        os.environ['DATABASE_URL'] = 'postgresql+asyncpg://u:p@localhost:5432/db'
        os.environ['SECRET_KEY'] = 'a-secret-key-that-is-at-least-32-characters!'
        os.environ['ENCRYPTION_KEY'] = 'encr-key-exactly-32-chars-long!!'

        from app.core.security import create_access_token
        from datetime import datetime, timedelta, timezone
        import jwt as pyjwt

        settings = Settings()
        payload = {
            'sub': 'usr-123',
            'tenant_id': 'tnt-456',
            'roles': [],
            'exp': datetime.now(timezone.utc) - timedelta(hours=1),
            'iat': datetime.now(timezone.utc) - timedelta(hours=2),
        }
        token = pyjwt.encode(payload, settings.secret_key, algorithm='HS256')

        with pytest.raises(pyjwt.ExpiredSignatureError):
            decode_token(token)

    def test_invalid_signature_raises_error(self):
        os.environ['DATABASE_URL'] = 'postgresql+asyncpg://u:p@localhost:5432/db'
        os.environ['SECRET_KEY'] = 'a-secret-key-that-is-at-least-32-characters!'
        os.environ['ENCRYPTION_KEY'] = 'encr-key-exactly-32-chars-long!!'

        from app.core.config import Settings
        settings = Settings()

        payload = {
            'sub': 'usr-123',
            'tenant_id': 'tnt-456',
            'roles': [],
            'exp': datetime.now(timezone.utc) + timedelta(hours=1),
            'iat': datetime.now(timezone.utc),
        }
        token = pyjwt.encode(payload, 'wrong-secret-key-that-is-32-characters!!', algorithm='HS256')

        with pytest.raises(pyjwt.InvalidSignatureError):
            decode_token(token)
