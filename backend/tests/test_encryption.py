import os

import pytest
from pydantic_core import ValidationError

from app.core.config import Settings
from app.core.exceptions import EncryptionError
from app.core.security import decrypt, encrypt


class TestEncryption:
    def test_round_trip(self):
        plaintext = '12345678'
        ciphertext = encrypt(plaintext)
        assert isinstance(ciphertext, str)
        assert decrypt(ciphertext) == plaintext

    def test_same_plaintext_produces_different_ciphertext(self):
        text = 'mismo_valor'
        c1 = encrypt(text)
        c2 = encrypt(text)
        assert c1 != c2

    def test_corrupted_nonce_raises_error(self):
        ciphertext = encrypt('test_data')
        if isinstance(ciphertext, str):
            corrupted = list(ciphertext)
            corrupted[0] = 'Z' if corrupted[0] != 'Z' else 'Y'
            corrupted_str = ''.join(corrupted)
        with pytest.raises(EncryptionError):
            decrypt(corrupted_str)

    def test_wrong_key_raises_error(self):
        ciphertext = encrypt('secret')
        original_key = os.environ.get('ENCRYPTION_KEY')
        os.environ['ENCRYPTION_KEY'] = 'd1ff3r3nt-k3y-3x4ctly-32-ch4rs!!'
        try:
            with pytest.raises(EncryptionError):
                decrypt(ciphertext)
        finally:
            if original_key:
                os.environ['ENCRYPTION_KEY'] = original_key
            else:
                del os.environ['ENCRYPTION_KEY']

    def test_encrypts_unicode(self):
        text = 'ñoñería 123 áéíóú'
        assert decrypt(encrypt(text)) == text

    def test_empty_string(self):
        assert decrypt(encrypt('')) == ''


class TestEncryptionKeyValidation:
    def test_rejects_key_shorter_than_32(self):
        os.environ['DATABASE_URL'] = 'postgresql+asyncpg://u:p@localhost:5432/db'
        os.environ['SECRET_KEY'] = 'a-secret-key-that-is-at-least-32-characters!'
        os.environ['ENCRYPTION_KEY'] = 'short'
        with pytest.raises(ValidationError):
            Settings()

    def test_rejects_key_longer_than_32(self):
        os.environ['DATABASE_URL'] = 'postgresql+asyncpg://u:p@localhost:5432/db'
        os.environ['SECRET_KEY'] = 'b-secret-key-that-is-at-least-32-characters!'
        os.environ['ENCRYPTION_KEY'] = 'this-key-is-way-too-long-for-encryption-purposes!!'
        with pytest.raises(ValidationError):
            Settings()

    def test_accepts_exactly_32_chars(self):
        os.environ['DATABASE_URL'] = 'postgresql+asyncpg://u:p@localhost:5432/db'
        os.environ['SECRET_KEY'] = 'c-secret-key-that-is-at-least-32-characters!'
        os.environ['ENCRYPTION_KEY'] = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        settings = Settings()
        assert len(settings.encryption_key) == 32
