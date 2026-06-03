from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.carreras import router as carreras_router
from app.api.v1.routers.cohortes import router as cohortes_router
from app.api.v1.routers.health import router as health_router
from app.api.v1.routers.materias import router as materias_router
from app.api.v1.routers.roles import router as roles_router
from app.api.v1.routers.permisos import router as permisos_router
from app.api.v1.routers.role_permisos import router as role_permisos_router
from app.api.v1.routers.user_roles import router as user_roles_router

__all__ = [
    'auth_router',
    'carreras_router',
    'cohortes_router',
    'health_router',
    'materias_router',
    'roles_router',
    'permisos_router',
    'role_permisos_router',
    'user_roles_router',
]
