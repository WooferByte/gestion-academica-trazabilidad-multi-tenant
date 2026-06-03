from app.repositories.asignacion import AsignacionRepository
from app.repositories.audit_repository import AuditRepository
from app.repositories.base import BaseRepository
from app.repositories.carrera import CarreraRepository
from app.repositories.cohorte import CohorteRepository
from app.repositories.evaluacion_repository import (
    ColoquioAlumnoRepository,
    EvaluacionRepository,
    ReservaEvaluacionRepository,
    ResultadoEvaluacionRepository,
    TurnoColoquioRepository,
)
from app.repositories.materia import MateriaRepository
from app.repositories.role import RoleRepository
from app.repositories.permission import PermissionRepository
from app.repositories.role_permission import RolePermissionRepository
from app.repositories.user_role import UserRoleRepository
from app.repositories.usuario import UsuarioRepository
from app.repositories.user_repository import UserRepository

__all__ = [
    'AsignacionRepository',
    'AuditRepository',
    'BaseRepository',
    'CarreraRepository',
    'CohorteRepository',
    'EvaluacionRepository',
    'TurnoColoquioRepository',
    'ReservaEvaluacionRepository',
    'ResultadoEvaluacionRepository',
    'ColoquioAlumnoRepository',
    'MateriaRepository',
    'RoleRepository',
    'PermissionRepository',
    'RolePermissionRepository',
    'UserRoleRepository',
    'UsuarioRepository',
    'UserRepository',
]
