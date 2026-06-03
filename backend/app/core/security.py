import base64
import hashlib
import os
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

import hashlib

from app.core.config import Settings
from app.core.exceptions import EncryptionError

pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')


def _get_key() -> bytes:
    settings = Settings()
    return settings.encryption_key.encode('utf-8')


def encrypt(plaintext: str) -> str:
    aesgcm = AESGCM(_get_key())
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
    return base64.b64encode(nonce + ciphertext).decode('utf-8')


def decrypt(payload: str) -> str:
    try:
        raw = base64.b64decode(payload.encode('utf-8'))
        nonce, ciphertext = raw[:12], raw[12:]
        aesgcm = AESGCM(_get_key())
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode('utf-8')
    except Exception as exc:
        raise EncryptionError('Error de cifrado/descifrado') from exc


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(
    user_id: str, tenant_id: str, roles: list[str],
    impersonator_id: str | None = None,
) -> str:
    settings = Settings()
    payload = {
        'sub': user_id,
        'tenant_id': tenant_id,
        'roles': roles,
        'exp': datetime.now(timezone.utc)
        + timedelta(minutes=settings.access_token_expire_minutes),
        'iat': datetime.now(timezone.utc),
    }
    if impersonator_id is not None:
        payload['impersonator_id'] = impersonator_id
    return jwt.encode(payload, settings.secret_key, algorithm='HS256')


def create_2fa_token(user_id: str, tenant_id: str) -> str:
    settings = Settings()
    payload = {
        'sub': user_id,
        'tenant_id': tenant_id,
        'purpose': '2fa',
        'exp': datetime.now(timezone.utc) + timedelta(minutes=5),
        'iat': datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.secret_key, algorithm='HS256')


def decode_token(token: str) -> dict:
    settings = Settings()
    return jwt.decode(token, settings.secret_key, algorithms=['HS256'])


def hash_email(email: str) -> str:
    settings = Settings()
    normalized = email.strip().lower()
    return hashlib.sha256(
        (normalized + settings.email_hash_salt).encode()
    ).hexdigest()


def hash_dni(dni: str) -> str:
    settings = Settings()
    normalized = dni.strip()
    return hashlib.sha256(
        (normalized + settings.email_hash_salt).encode()
    ).hexdigest()
