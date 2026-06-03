from app.repositories.audit_repository import AuditRepository
from app.repositories.base import BaseRepository
from app.repositories.carrera import CarreraRepository
from app.repositories.cohorte import CohorteRepository
from app.repositories.materia import MateriaRepository
from app.repositories.role import RoleRepository
from app.repositories.permission import PermissionRepository
from app.repositories.role_permission import RolePermissionRepository
from app.repositories.user_role import UserRoleRepository

__all__ = [
    'AuditRepository',
    'BaseRepository',
    'CarreraRepository',
    'CohorteRepository',
    'MateriaRepository',
    'RoleRepository',
    'PermissionRepository',
    'RolePermissionRepository',
    'UserRoleRepository',
]
