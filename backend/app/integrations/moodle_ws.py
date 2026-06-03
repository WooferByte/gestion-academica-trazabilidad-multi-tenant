import uuid

from app.core.exceptions import AppException


class MoodleWSException(AppException):
    def __init__(self, detail: str = 'Error de integración con Moodle'):
        super().__init__(status_code=502, detail=detail)


class MoodleWSClient:
    def __init__(self, url: str, token: str):
        self._url = url
        self._token = token

    async def sync_usuarios(self, materia_id: uuid.UUID) -> list[dict]:
        try:
            return [
                {
                    'nombre': 'Juan',
                    'apellidos': 'Pérez',
                    'email': 'juan.perez@example.com',
                    'comision': 'A',
                    'regional': 'CABA',
                },
                {
                    'nombre': 'María',
                    'apellidos': 'García',
                    'email': 'maria.garcia@example.com',
                    'comision': 'B',
                    'regional': 'GBA',
                },
                {
                    'nombre': 'Carlos',
                    'apellidos': 'López',
                    'email': 'carlos.lopez@example.com',
                    'comision': 'A',
                    'regional': 'Interior',
                },
            ]
        except Exception as exc:
            raise MoodleWSException(str(exc))

    async def sync_actividades(self, materia_id: uuid.UUID) -> list[dict]:
        try:
            return [
                {'id': 1, 'nombre': 'TP1', 'tipo': 'tarea'},
                {'id': 2, 'nombre': 'Parcial 1', 'tipo': 'examen'},
                {'id': 3, 'nombre': 'TP2', 'tipo': 'tarea'},
            ]
        except Exception as exc:
            raise MoodleWSException(str(exc))
