from fastapi import HTTPException


class AppException(HTTPException):
    def __init__(self, status_code: int, detail: str | None = None):
        super().__init__(status_code=status_code, detail=detail)


class TenantNotFoundException(AppException):
    def __init__(self, detail: str | None = None):
        super().__init__(status_code=404, detail=detail or 'Tenant no encontrado')


class EncryptionError(AppException):
    def __init__(self, detail: str | None = None):
        super().__init__(status_code=500, detail=detail or 'Error de cifrado/descifrado')


class SoftDeletedException(AppException):
    def __init__(self, detail: str | None = None):
        super().__init__(status_code=409, detail=detail or 'El registro fue eliminado')
