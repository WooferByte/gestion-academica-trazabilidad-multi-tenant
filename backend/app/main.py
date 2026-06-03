from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.routers.admin_usuarios import router as admin_usuarios_router
from app.api.v1.routers.asignaciones import router as asignaciones_router
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.auth_impersonation import router as auth_impersonation_router
from app.api.v1.routers.carreras import router as carreras_router
from app.api.v1.routers.cohortes import router as cohortes_router
from app.api.v1.routers.equipos import router as equipos_router
from app.api.v1.routers.health import router as health_router
from app.api.v1.routers.materias import router as materias_router
from app.api.v1.routers.permisos import router as permisos_router
from app.api.v1.routers.role_permisos import router as role_permisos_router
from app.api.v1.routers.roles import router as roles_router
from app.api.v1.routers.user_roles import router as user_roles_router
from app.core.config import Settings
from app.core.database import dispose_engine, init_engine
from app.core.logging import setup_json_logging
from app.core.observability import setup_observability


@asynccontextmanager
async def lifespan(app_instance: FastAPI) -> AsyncGenerator[None, None]:
    settings = Settings()
    init_engine(str(settings.database_url))
    setup_json_logging()
    setup_observability(app_instance)
    yield
    await dispose_engine()


def create_app() -> FastAPI:
    app_instance = FastAPI(title='activia-trace', version='0.1.0', lifespan=lifespan)
    app_instance.include_router(health_router)
    app_instance.include_router(auth_router)
    app_instance.include_router(auth_impersonation_router)
    app_instance.include_router(admin_usuarios_router)
    app_instance.include_router(asignaciones_router)
    app_instance.include_router(carreras_router)
    app_instance.include_router(cohortes_router)
    app_instance.include_router(equipos_router)
    app_instance.include_router(materias_router)
    app_instance.include_router(roles_router)
    app_instance.include_router(permisos_router)
    app_instance.include_router(role_permisos_router)
    app_instance.include_router(user_roles_router)
    return app_instance


app = create_app()
