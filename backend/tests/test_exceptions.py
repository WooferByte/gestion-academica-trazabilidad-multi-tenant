import pytest
from fastapi import HTTPException

from app.core.exceptions import (
    AppException,
    EncryptionError,
    SoftDeletedException,
    TenantNotFoundException,
)


class TestExceptions:
    def test_app_exception_extends_http_exception(self):
        exc = AppException(status_code=400, detail='test')
        assert isinstance(exc, HTTPException)
        assert exc.status_code == 400
        assert exc.detail == 'test'

    def test_tenant_not_found_is_404(self):
        exc = TenantNotFoundException()
        assert exc.status_code == 404
        assert 'Tenant' in exc.detail or 'no encontrado' in exc.detail

    def test_tenant_not_found_custom_message(self):
        exc = TenantNotFoundException(detail='Custom msg')
        assert exc.status_code == 404
        assert exc.detail == 'Custom msg'

    def test_encryption_error_is_500(self):
        exc = EncryptionError()
        assert exc.status_code == 500
        assert 'Error de cifrado' in exc.detail

    def test_encryption_error_custom_message(self):
        exc = EncryptionError(detail='Custom crypto error')
        assert exc.status_code == 500
        assert exc.detail == 'Custom crypto error'

    def test_soft_deleted_is_409(self):
        exc = SoftDeletedException()
        assert exc.status_code == 409
        assert 'eliminado' in exc.detail or 'deleted' in exc.detail

    def test_soft_deleted_custom_message(self):
        exc = SoftDeletedException(detail='Custom delete msg')
        assert exc.status_code == 409
        assert exc.detail == 'Custom delete msg'


class TestExceptionsInIsolation:
    def test_exceptions_are_distinct_types(self):
        exc_404 = TenantNotFoundException()
        exc_500 = EncryptionError()
        exc_409 = SoftDeletedException()
        assert type(exc_404) is TenantNotFoundException
        assert type(exc_500) is EncryptionError
        assert type(exc_409) is SoftDeletedException
        assert exc_404.status_code != exc_500.status_code
        assert exc_500.status_code != exc_409.status_code
