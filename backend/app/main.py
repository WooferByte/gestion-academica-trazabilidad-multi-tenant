from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers.admin_usuarios import router as admin_usuarios_router
from app.api.v1.routers.avisos import router as avisos_router
from app.api.v1.routers.tareas import router as tareas_router
from app.api.v1.routers.tareas import admin_router as tareas_admin_router
from app.api.v1.routers.asignaciones import router as asignaciones_router
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.auth_impersonation import router as auth_impersonation_router
from app.api.v1.routers.carreras import router as carreras_router
from app.api.v1.routers.categorias_plus import router as categorias_plus_router
from app.api.v1.routers.cohortes import router as cohortes_router
from app.api.v1.routers.equipos import router as equipos_router
from app.api.v1.routers.comunicaciones import router as comunicaciones_router
from app.api.v1.routers.health import router as health_router
from app.api.v1.routers.materia_categoria import router as materia_categoria_router
from app.api.v1.routers.materias import router as materias_router
from app.api.v1.routers.padron import router as padron_router
from app.api.v1.routers.calificaciones import router as calificaciones_router
from app.api.v1.routers.umbral import router as umbral_router
from app.api.v1.routers.permisos import router as permisos_router
from app.api.v1.routers.role_permisos import router as role_permisos_router
from app.api.v1.routers.roles import router as roles_router
from app.api.v1.routers.user_roles import router as user_roles_router
from app.api.v1.routers.encuentros import router as encuentros_router
from app.api.v1.routers.guardias import router as guardias_router
from app.api.v1.routers.coloquios import router as coloquios_router
from app.api.v1.routers.programas import router as programas_router
from app.api.v1.routers.fechas_academicas import router as fechas_academicas_router
from app.api.v1.routers.grilla_salarial import router as grilla_salarial_router
from app.api.v1.routers.liquidaciones import router as liquidaciones_router
from app.api.v1.routers.facturas import router as facturas_router
from app.core.config import Settings
from app.core.database import dispose_engine, init_engine
from app.core.logging import setup_json_logging
from app.core.observability import setup_observability
from app.core.rate_limit_middleware import RateLimitMiddleware
from app.core.security_headers_middleware import SecurityHeadersMiddleware


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
    settings = Settings()

    origins = [
        o.strip()
        for o in settings.cors_origins.split(',')
        if o.strip()
    ]
    app_instance.add_middleware(
        SecurityHeadersMiddleware,
        debug=settings.debug,
    )
    app_instance.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
        allow_headers=['Authorization', 'Content-Type', 'X-Requested-With', 'Accept'],
    )
    app_instance.add_middleware(
        RateLimitMiddleware,
        max_requests=settings.rate_limit_max_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )
    app_instance.include_router(avisos_router)
    app_instance.include_router(comunicaciones_router)
    app_instance.include_router(health_router)
    app_instance.include_router(auth_router)
    app_instance.include_router(auth_impersonation_router)
    app_instance.include_router(admin_usuarios_router)
    app_instance.include_router(asignaciones_router)
    app_instance.include_router(carreras_router)
    app_instance.include_router(categorias_plus_router)
    app_instance.include_router(cohortes_router)
    app_instance.include_router(equipos_router)
    app_instance.include_router(materia_categoria_router)
    app_instance.include_router(materias_router)
    app_instance.include_router(roles_router)
    app_instance.include_router(padron_router)
    app_instance.include_router(permisos_router)
    app_instance.include_router(role_permisos_router)
    app_instance.include_router(user_roles_router)
    app_instance.include_router(calificaciones_router)
    app_instance.include_router(umbral_router)
    app_instance.include_router(encuentros_router)
    app_instance.include_router(guardias_router)
    app_instance.include_router(coloquios_router)
    app_instance.include_router(programas_router)
    app_instance.include_router(fechas_academicas_router)
    app_instance.include_router(tareas_router)
    app_instance.include_router(tareas_admin_router)
    app_instance.include_router(grilla_salarial_router)
    app_instance.include_router(liquidaciones_router)
    app_instance.include_router(facturas_router)
    from app.api.v1.routers.analisis_router import router as analisis_router
    app_instance.include_router(analisis_router)
    return app_instance


app = create_app()
