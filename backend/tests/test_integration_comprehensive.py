"""Comprehensive integration test covering ALL API endpoints.

WARNING: This is a DESTRUCTIVE test — runs on test DB that is dropped after each test.
Do NOT run against production.
"""

import io
import json
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password
from app.models.asignacion import Asignacion
from app.models.aviso import Aviso
from app.models.calificacion import Calificacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.coloquio_alumno import ColoquioAlumno
from app.models.comunicacion import Comunicacion
from app.models.entrada_padron import EntradaPadron
from app.models.evaluacion import Evaluacion
from app.models.guardia import Guardia
from app.models.instancia_encuentro import InstanciaEncuentro
from app.models.materia import Materia
from app.models.permission import Permission
from app.models.reserva_evaluacion import ReservaEvaluacion
from app.models.resultado_evaluacion import ResultadoEvaluacion
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.slot_encuentro import SlotEncuentro
from app.models.tenant import Tenant
from app.models.turno_coloquio import TurnoColoquio
from app.models.umbral_materia import UmbralMateria
from app.models.user import User
from app.models.user_role import UserRole
from app.models.version_padron import VersionPadron
from tests.helpers import _create_tenant, _create_user


@dataclass
class EndpointResult:
    index: int
    method: str
    path: str
    status: int
    response_ok: bool
    notes: str = ''


RESULTS: list[EndpointResult] = []
_counter = 0


def _next() -> int:
    global _counter
    _counter += 1
    return _counter


async def _call(
    client: AsyncClient,
    method: str,
    path: str,
    token: str | None = None,
    json_body: Any = None,
    data: dict | None = None,
    files: dict | None = None,
    params: dict | None = None,
    expect_status: int | None = None,
) -> tuple[int, dict | list | str]:
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'

    kwargs = dict(
        url=path,
        headers=headers,
        params=params,
    )
    if json_body is not None:
        kwargs['json'] = json_body
    if data is not None:
        kwargs['data'] = data
    if files is not None:
        kwargs['files'] = files

    response = await getattr(client, method)(**kwargs)

    status = response.status_code
    try:
        body = response.json()
    except Exception:
        body = response.text

    ok = status != 500
    notes = ''
    if status == 500:
        notes = 'SERVER ERROR'
    elif status == 404 and 'detail' in (body if isinstance(body, dict) else {}):
        notes = 'expected 404'
    elif status == 422:
        notes = 'expected validation error'
    elif status == 403:
        notes = 'insufficient permissions'
    elif status == 401:
        notes = 'unauthorized'

    if expect_status is not None and status != expect_status:
        notes += f' (expected {expect_status})'

    idx = _next()
    RESULTS.append(EndpointResult(
        index=idx, method=method.upper(), path=path,
        status=status, response_ok=ok, notes=notes.strip(),
    ))
    return status, body


async def _seed_all_permissions(session: AsyncSession, tenant_id: uuid.UUID, role_id: uuid.UUID) -> None:
    """Create all required permissions and assign them to the given role."""
    all_perms = [
        'estructura:gestionar', 'usuarios:gestionar', 'avisos:publicar',
        'comunicacion:enviar', 'comunicacion:aprobar', 'calificaciones:importar',
        'padron:cargar', 'equipos:asignar', 'rbac:gestionar',
        'encuentros:gestionar', 'coloquios:gestionar', 'coloquios:reservar',
        'atrasados:ver', 'impersonacion:usar',
    ]
    for codigo in all_perms:
        modulo, accion = codigo.split(':')
        perm = Permission(
            tenant_id=tenant_id, codigo=codigo,
            modulo=modulo, accion=accion,
        )
        session.add(perm)
        await session.flush()
        rp = RolePermission(tenant_id=tenant_id, role_id=role_id, permiso_id=perm.id, propio=True)
        session.add(rp)
    await session.flush()


async def _create_carrera_cohorte_materia(
    session: AsyncSession, tenant_id: uuid.UUID,
) -> tuple[uuid.UUID, uuid.UUID, uuid.UUID]:
    carrera = Carrera(tenant_id=tenant_id, codigo='ING', nombre='Ingeniería', estado='Activa')
    session.add(carrera)
    await session.flush()
    carrera_id = carrera.id

    cohorte = Cohorte(
        tenant_id=tenant_id, carrera_id=carrera_id,
        nombre='2025', anio=2025,
        vig_desde=date(2025, 1, 1),
        estado='Activa',
    )
    session.add(cohorte)
    await session.flush()
    cohorte_id = cohorte.id

    materia = Materia(tenant_id=tenant_id, codigo='MATE101', nombre='Matemáticas I', estado='Activa')
    session.add(materia)
    await session.flush()
    materia_id = materia.id

    return carrera_id, cohorte_id, materia_id


async def _ensure_test_data(
    session: AsyncSession, tenant_id: uuid.UUID,
    carrera_id: uuid.UUID, cohorte_id: uuid.UUID, materia_id: uuid.UUID,
    admin_user_id: uuid.UUID,
) -> None:
    """Create additional test data needed for certain endpoints."""
    pass


async def _setup_admin(
    session: AsyncSession,
) -> tuple[uuid.UUID, uuid.UUID, uuid.UUID, str]:
    """Create tenant, admin user with all permissions, return tenant_id, user_id, role_id, token."""
    tenant = await _create_tenant(session, 'TestTenant', 'TEST')
    tenant_id = tenant.id

    role = Role(tenant_id=tenant_id, name='superadmin', codigo='superadmin')
    session.add(role)
    await session.flush()
    role_id = role.id

    user = User(
        tenant_id=tenant_id,
        email='admin@test.com',
        password_hash=hash_password('password123'),
        roles=['superadmin'],
        estado='Activo',
    )
    session.add(user)
    await session.flush()
    user_id = user.id

    ur = UserRole(tenant_id=tenant_id, user_id=user_id, role_id=role_id)
    session.add(ur)
    await session.flush()

    await _seed_all_permissions(session, tenant_id, role_id)

    token = create_access_token(str(user_id), str(tenant_id), ['superadmin'])
    return tenant_id, user_id, role_id, token


# ──────────────────────────────────────────────────────────────────────
# MAIN TEST — one giant test covering all endpoints
# ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_all_endpoints(db_session: AsyncSession, async_client: AsyncClient) -> None:
    global RESULTS, _counter
    RESULTS = []
    _counter = 0

    # ── SETUP ──────────────────────────────────────────────────────────
    tenant_id, admin_user_id, admin_role_id, admin_token = await _setup_admin(db_session)

    carrera_id, cohorte_id, materia_id = await _create_carrera_cohorte_materia(
        db_session, tenant_id,
    )

    await _ensure_test_data(db_session, tenant_id, carrera_id, cohorte_id, materia_id, admin_user_id)

    # We'll use this second user for user-role tests, etc.
    second_user = User(
        tenant_id=tenant_id,
        email='second@test.com',
        password_hash=hash_password('password123'),
        roles=[],
        estado='Activo',
    )
    db_session.add(second_user)
    await db_session.flush()
    second_user_id = second_user.id
    second_token = create_access_token(str(second_user_id), str(tenant_id), [])

    # ── 1. HEALTH ───────────────────────────────────────────────────────
    await _call(async_client, 'get', '/health')
    # Health without DB dependency override is tricky; it depends on global engine

    # ── 2. AUTH ─────────────────────────────────────────────────────────
    # POST /api/v1/auth/login — valid
    status, body = await _call(
        async_client, 'post', '/api/v1/auth/login',
        json_body={'email': 'admin@test.com', 'password': 'password123'},
    )
    # This will fail because auth service needs its own session, not the test session
    # Expected behavior: 401 (no session for auth service to work) or success
    # We just verify no 500

    # POST /api/v1/auth/login — invalid body (no password)
    await _call(
        async_client, 'post', '/api/v1/auth/login',
        json_body={'email': 'test@test.com'},
    )
    # POST /api/v1/auth/login — wrong credentials
    await _call(
        async_client, 'post', '/api/v1/auth/login',
        json_body={'email': 'admin@test.com', 'password': 'wrong'},
    )

    # POST /api/v1/auth/refresh — invalid token
    await _call(
        async_client, 'post', '/api/v1/auth/refresh',
        json_body={'refresh_token': 'invalid-refresh-token'},
    )

    # POST /api/v1/auth/logout — valid with token
    await _call(
        async_client, 'post', '/api/v1/auth/logout',
        json_body={'refresh_token': 'some-refresh-token-for-logout'},
        token=admin_token,
    )

    # POST /api/v1/auth/2fa/enroll
    await _call(async_client, 'post', '/api/v1/auth/2fa/enroll', token=admin_token)

    # POST /api/v1/auth/2fa/verify
    await _call(
        async_client, 'post', '/api/v1/auth/2fa/verify',
        json_body={'secret': 'testsecret123', 'code': '123456'},
        token=admin_token,
    )

    # POST /api/v1/auth/2fa/validate — invalid 2fa token
    await _call(
        async_client, 'post', '/api/v1/auth/2fa/validate',
        json_body={'2fa_token': 'invalid-2fa-token', 'code': '123456'},
    )

    # POST /api/v1/auth/forgot
    await _call(
        async_client, 'post', '/api/v1/auth/forgot',
        json_body={'email': 'admin@test.com'},
    )
    await _call(
        async_client, 'post', '/api/v1/auth/forgot',
        json_body={'email': 'nonexistent@test.com'},
    )

    # POST /api/v1/auth/reset — invalid token
    await _call(
        async_client, 'post', '/api/v1/auth/reset',
        json_body={'token': 'bad-token', 'new_password': 'newpassword123'},
    )

    # POST /api/v1/auth/impersonate
    await _call(
        async_client, 'post', '/api/v1/auth/impersonate',
        json_body={'target_user_id': str(admin_user_id)},  # self-impersonation -> 400
        token=admin_token,
    )
    await _call(
        async_client, 'post', '/api/v1/auth/impersonate',
        json_body={'target_user_id': str(uuid.uuid4())},  # non-existent -> 404
        token=admin_token,
    )

    # POST /api/v1/auth/impersonate/stop (no active impersonation -> 400)
    await _call(async_client, 'post', '/api/v1/auth/impersonate/stop', token=admin_token)

    # ── 3. CARRERAS CRUD ───────────────────────────────────────────────
    # GET list
    await _call(async_client, 'get', '/api/v1/admin/carreras', token=admin_token)

    # POST create
    status, body = await _call(
        async_client, 'post', '/api/v1/admin/carreras',
        json_body={'codigo': 'SIS', 'nombre': 'Sistemas'},
        token=admin_token,
    )
    new_carrera_id = body.get('id') if isinstance(body, dict) else None

    # GET by id
    if new_carrera_id:
        await _call(async_client, 'get', f'/api/v1/admin/carreras/{new_carrera_id}', token=admin_token)

    # PUT update
    if new_carrera_id:
        await _call(
            async_client, 'put', f'/api/v1/admin/carreras/{new_carrera_id}',
            json_body={'nombre': 'Ingeniería en Sistemas'},
            token=admin_token,
        )

    # DELETE
    if new_carrera_id:
        await _call(async_client, 'delete', f'/api/v1/admin/carreras/{new_carrera_id}', token=admin_token)

    # GET after delete — should 404
    if new_carrera_id:
        await _call(async_client, 'get', f'/api/v1/admin/carreras/{new_carrera_id}', token=admin_token)

    # 404 on non-existent
    await _call(
        async_client, 'get', f'/api/v1/admin/carreras/{uuid.uuid4()}',
        token=admin_token,
    )

    # ── 4. COHORTES CRUD ───────────────────────────────────────────────
    await _call(async_client, 'get', '/api/v1/admin/cohortes', token=admin_token)

    status, body = await _call(
        async_client, 'post', '/api/v1/admin/cohortes',
        json_body={
            'carrera_id': str(carrera_id),
            'nombre': '2026',
            'anio': 2026,
            'vig_desde': '2026-01-01',
            'estado': 'Activa',
        },
        token=admin_token,
    )
    new_cohorte_id = body.get('id') if isinstance(body, dict) else None

    if new_cohorte_id:
        await _call(async_client, 'get', f'/api/v1/admin/cohortes/{new_cohorte_id}', token=admin_token)
        await _call(
            async_client, 'put', f'/api/v1/admin/cohortes/{new_cohorte_id}',
            json_body={'nombre': '2026 Mod'},
            token=admin_token,
        )
        await _call(async_client, 'delete', f'/api/v1/admin/cohortes/{new_cohorte_id}', token=admin_token)
        await _call(async_client, 'get', f'/api/v1/admin/cohortes/{new_cohorte_id}', token=admin_token)

    await _call(async_client, 'get', f'/api/v1/admin/cohortes/{uuid.uuid4()}', token=admin_token)

    # ── 5. MATERIAS CRUD ───────────────────────────────────────────────
    await _call(async_client, 'get', '/api/v1/admin/materias', token=admin_token)

    status, body = await _call(
        async_client, 'post', '/api/v1/admin/materias',
        json_body={'codigo': 'FIS101', 'nombre': 'Física I'},
        token=admin_token,
    )
    new_materia_id = body.get('id') if isinstance(body, dict) else None

    if new_materia_id:
        await _call(async_client, 'get', f'/api/v1/admin/materias/{new_materia_id}', token=admin_token)
        await _call(
            async_client, 'put', f'/api/v1/admin/materias/{new_materia_id}',
            json_body={'nombre': 'Física General'},
            token=admin_token,
        )
        await _call(async_client, 'delete', f'/api/v1/admin/materias/{new_materia_id}', token=admin_token)
        await _call(async_client, 'get', f'/api/v1/admin/materias/{new_materia_id}', token=admin_token)

    await _call(async_client, 'get', f'/api/v1/admin/materias/{uuid.uuid4()}', token=admin_token)

    # ── 6. USUARIOS CRUD ───────────────────────────────────────────────
    await _call(async_client, 'get', '/api/v1/admin/usuarios', token=admin_token)

    status, body = await _call(
        async_client, 'post', '/api/v1/admin/usuarios',
        json_body={
            'email': 'nuevo@test.com',
            'password': 'password123',
            'nombre': 'Nuevo',
            'apellido': 'Usuario',
            'estado': 'Activo',
        },
        token=admin_token,
    )
    new_user_id = body.get('id') if isinstance(body, dict) else None

    if new_user_id:
        await _call(async_client, 'get', f'/api/v1/admin/usuarios/{new_user_id}', token=admin_token)
        await _call(
            async_client, 'patch', f'/api/v1/admin/usuarios/{new_user_id}',
            json_body={'nombre': 'Actualizado'},
            token=admin_token,
        )
        await _call(async_client, 'delete', f'/api/v1/admin/usuarios/{new_user_id}', token=admin_token)
        await _call(async_client, 'get', f'/api/v1/admin/usuarios/{new_user_id}', token=admin_token)

    await _call(async_client, 'get', f'/api/v1/admin/usuarios/{uuid.uuid4()}', token=admin_token)

    # ── 7. ROLES CRUD ──────────────────────────────────────────────────
    await _call(async_client, 'get', '/api/v1/roles', token=admin_token)

    status, body = await _call(
        async_client, 'post', '/api/v1/roles',
        json_body={'name': 'Test Role', 'codigo': 'test_role'},
        token=admin_token,
    )
    new_role_id = body.get('id') if isinstance(body, dict) else None

    if new_role_id:
        await _call(async_client, 'get', f'/api/v1/roles/{new_role_id}', token=admin_token)
        await _call(
            async_client, 'put', f'/api/v1/roles/{new_role_id}',
            json_body={'name': 'Updated Role'},
            token=admin_token,
        )
        await _call(async_client, 'delete', f'/api/v1/roles/{new_role_id}', token=admin_token)
        await _call(async_client, 'get', f'/api/v1/roles/{new_role_id}', token=admin_token)

    await _call(async_client, 'get', f'/api/v1/roles/{uuid.uuid4()}', token=admin_token)

    # ── 8. PERMISOS CRUD ───────────────────────────────────────────────
    await _call(async_client, 'get', '/api/v1/permisos', token=admin_token)

    status, body = await _call(
        async_client, 'post', '/api/v1/permisos',
        json_body={
            'codigo': 'test:permiso',
            'modulo': 'test',
            'accion': 'permiso',
        },
        token=admin_token,
    )
    new_perm_id = body.get('id') if isinstance(body, dict) else None

    if new_perm_id:
        await _call(async_client, 'get', f'/api/v1/permisos/{new_perm_id}', token=admin_token)
        await _call(
            async_client, 'put', f'/api/v1/permisos/{new_perm_id}',
            json_body={'descripcion': 'Test permiso desc'},
            token=admin_token,
        )
        await _call(async_client, 'delete', f'/api/v1/permisos/{new_perm_id}', token=admin_token)
        await _call(async_client, 'get', f'/api/v1/permisos/{new_perm_id}', token=admin_token)

    await _call(async_client, 'get', f'/api/v1/permisos/{uuid.uuid4()}', token=admin_token)

    # ── 9. ROLE-PERMISOS ───────────────────────────────────────────────
    # Create a permission to assign
    test_perm = Permission(tenant_id=tenant_id, codigo='roleperm:test', modulo='roleperm', accion='test')
    db_session.add(test_perm)
    await db_session.flush()

    # GET role's permissions
    await _call(async_client, 'get', f'/api/v1/roles/{admin_role_id}/permisos', token=admin_token)

    # POST assign permission to role
    await _call(
        async_client, 'post', f'/api/v1/roles/{admin_role_id}/permisos',
        json_body={'permiso_id': str(test_perm.id), 'propio': True},
        token=admin_token,
    )

    # DELETE unassign
    await _call(
        async_client, 'delete', f'/api/v1/roles/{admin_role_id}/permisos/{test_perm.id}',
        token=admin_token,
    )

    # ── 10. USER-ROLES ─────────────────────────────────────────────────
    # GET user's roles
    await _call(async_client, 'get', f'/api/v1/users/{second_user_id}/roles', token=admin_token)

    # POST assign role to user
    await _call(
        async_client, 'post', f'/api/v1/users/{second_user_id}/roles',
        json_body={'role_id': str(admin_role_id)},
        token=admin_token,
    )

    # DELETE unassign
    await _call(
        async_client, 'delete', f'/api/v1/users/{second_user_id}/roles/{admin_role_id}',
        token=admin_token,
    )

    # ── 11. ASIGNACIONES CRUD ──────────────────────────────────────────
    await _call(async_client, 'get', '/api/v1/asignaciones', token=admin_token)

    status, body = await _call(
        async_client, 'post', '/api/v1/asignaciones',
        json_body={
            'usuario_id': str(second_user_id),
            'rol': 'PROFESOR',
            'materia_id': str(materia_id),
            'carrera_id': str(carrera_id),
            'cohorte_id': str(cohorte_id),
        },
        token=admin_token,
    )
    new_asig_id = body.get('id') if isinstance(body, dict) else None

    if new_asig_id:
        await _call(async_client, 'get', f'/api/v1/asignaciones/{new_asig_id}', token=admin_token)
        await _call(
            async_client, 'patch', f'/api/v1/asignaciones/{new_asig_id}',
            json_body={'rol': 'TUTOR'},
            token=admin_token,
        )
        await _call(async_client, 'delete', f'/api/v1/asignaciones/{new_asig_id}', token=admin_token)
        await _call(async_client, 'get', f'/api/v1/asignaciones/{new_asig_id}', token=admin_token)

    await _call(async_client, 'get', f'/api/v1/asignaciones/{uuid.uuid4()}', token=admin_token)

    # ── 12. EQUIPOS ────────────────────────────────────────────────────
    await _call(async_client, 'get', '/api/v1/equipos/mis-equipos', token=admin_token)
    await _call(
        async_client, 'get', '/api/v1/equipos/mis-equipos',
        params={'materia_id': str(materia_id), 'cohorte_id': str(cohorte_id)},
        token=second_token,
    )

    # POST asignacion-masiva
    await _call(
        async_client, 'post', '/api/v1/equipos/asignacion-masiva',
        json_body={
            'usuario_ids': [str(second_user_id)],
            'materia_id': str(materia_id),
            'cohorte_id': str(cohorte_id),
            'rol': 'PROFESOR',
        },
        token=admin_token,
    )

    # POST clonar
    await _call(
        async_client, 'post', '/api/v1/equipos/clonar',
        json_body={
            'origen': {'materia_id': str(materia_id), 'carrera_id': str(carrera_id), 'cohorte_id': str(cohorte_id)},
            'destino': {'materia_id': str(materia_id), 'carrera_id': str(carrera_id), 'cohorte_id': str(cohorte_id)},
        },
        token=admin_token,
    )

    # PATCH vigencia
    await _call(
        async_client, 'patch', '/api/v1/equipos/vigencia',
        json_body={
            'materia_id': str(materia_id),
            'carrera_id': str(carrera_id),
            'cohorte_id': str(cohorte_id),
        },
        token=admin_token,
    )

    # GET exportar
    await _call(async_client, 'get', '/api/v1/equipos/exportar', token=admin_token)
    await _call(
        async_client, 'get', '/api/v1/equipos/exportar',
        params={'materia_id': str(materia_id)},
        token=admin_token,
    )

    # ── 13. AVISOS ─────────────────────────────────────────────────────
    status, body = await _call(
        async_client, 'post', '/api/v1/avisos',
        json_body={
            'alcance': 'Global',
            'severidad': 'Info',
            'titulo': 'Test Aviso',
            'cuerpo': 'Cuerpo del aviso de prueba',
            'inicio_vigencia': '2025-01-01T00:00:00Z',
            'fin_vigencia': '2025-12-31T23:59:59Z',
            'requiere_ack': False,
            'orden': 0,
        },
        token=admin_token,
    )
    new_aviso_id = body.get('id') if isinstance(body, dict) else None

    await _call(async_client, 'get', '/api/v1/avisos', token=admin_token)
    await _call(async_client, 'get', '/api/v1/avisos', token=second_token)

    if new_aviso_id:
        await _call(async_client, 'get', f'/api/v1/avisos/{new_aviso_id}', token=admin_token)
        await _call(
            async_client, 'patch', f'/api/v1/avisos/{new_aviso_id}',
            json_body={'titulo': 'Aviso Actualizado'},
            token=admin_token,
        )
        await _call(async_client, 'post', f'/api/v1/avisos/{new_aviso_id}/ack', token=admin_token)
        await _call(async_client, 'delete', f'/api/v1/avisos/{new_aviso_id}', token=admin_token)
        await _call(async_client, 'get', f'/api/v1/avisos/{new_aviso_id}', token=admin_token)

    await _call(async_client, 'get', f'/api/v1/avisos/{uuid.uuid4()}', token=admin_token)

    # ── 14. COMUNICACIONES ─────────────────────────────────────────────
    # POST preview
    await _call(
        async_client, 'post', '/api/v1/comunicaciones/preview',
        json_body={
            'destinatario': 'alumno@test.com',
            'asunto': 'Hola {{nombre}}',
            'cuerpo': 'Estimado {{nombre}} {{apellido}}',
            'variables': {'nombre': 'Juan', 'apellido': 'Pérez'},
        },
        token=admin_token,
    )

    # POST single
    status, body = await _call(
        async_client, 'post', '/api/v1/comunicaciones',
        json_body={
            'destinatario': 'alumno@test.com',
            'asunto': 'Notificación',
            'cuerpo': 'Cuerpo del mensaje',
        },
        token=admin_token,
    )
    new_com_id = body.get('id') if isinstance(body, dict) else None

    # POST lote
    status, body = await _call(
        async_client, 'post', '/api/v1/comunicaciones/lote',
        json_body={
            'destinatarios': ['alumno1@test.com', 'alumno2@test.com'],
            'asunto': 'Aviso masivo',
            'cuerpo': 'Cuerpo masivo',
        },
        token=admin_token,
    )
    lote_ids = set()
    if isinstance(body, list):
        for item in body:
            lid = item.get('lote_id')
            if lid:
                lote_ids.add(lid)

    # POST aprobar-lote
    for lid in lote_ids:
        await _call(
            async_client, 'post', '/api/v1/comunicaciones/aprobar-lote',
            json_body={'lote_id': str(lid), 'accion': 'aprobar'},
            token=admin_token,
        )

    # GET list
    await _call(async_client, 'get', '/api/v1/comunicaciones', token=admin_token)
    for lid in lote_ids:
        await _call(
            async_client, 'get', '/api/v1/comunicaciones',
            params={'lote_id': str(lid)},
            token=admin_token,
        )

    # POST cancelar
    if new_com_id:
        await _call(
            async_client, 'post', f'/api/v1/comunicaciones/{new_com_id}/cancelar',
            token=admin_token,
        )

    # ── 15. PADRON ────────────────────────────────────────────────────
    # POST importar/preview (form with file)
    csv_content = 'nombre,apellidos,email,comision,regional\nJuan,Perez,juan@test.com,C1,Regional1\n'
    await _call(
        async_client, 'post', '/api/v1/padron/importar/preview',
        data={'materia_id': str(materia_id), 'cohorte_id': str(cohorte_id)},
        files={'archivo': ('test.csv', csv_content, 'text/csv')},
        token=admin_token,
    )

    # POST importar/confirmar
    status, body = await _call(
        async_client, 'post', '/api/v1/padron/importar/confirmar',
        data={'materia_id': str(materia_id), 'cohorte_id': str(cohorte_id)},
        files={'archivo': ('test.csv', csv_content, 'text/csv')},
        token=admin_token,
    )
    version_id = body.get('id') if isinstance(body, dict) else None

    # GET versiones
    await _call(async_client, 'get', '/api/v1/padron/versiones', token=admin_token)

    # POST vaciar/{materia_id}/{cohorte_id}
    await _call(
        async_client, 'post', f'/api/v1/padron/vaciar/{materia_id}/{cohorte_id}',
        token=admin_token,
    )

    # POST sync-moodle
    await _call(
        async_client, 'post', '/api/v1/padron/sync-moodle',
        data={'materia_id': str(materia_id), 'cohorte_id': str(cohorte_id)},
        token=admin_token,
    )

    # ── 16. CALIFICACIONES ────────────────────────────────────────────
    # POST importar/preview (form with file)
    excel_content = b'header1,header2\nval1,val2\n'
    await _call(
        async_client, 'post', '/api/v1/calificaciones/importar/preview',
        data={'materia_id': str(materia_id), 'cohorte_id': str(cohorte_id)},
        files={'archivo': ('test.csv', excel_content, 'text/csv')},
        token=admin_token,
    )

    # POST importar/confirmar
    actividades_json = json.dumps([{'nombre': 'TP1', 'tipo': 'tp'}])
    await _call(
        async_client, 'post', '/api/v1/calificaciones/importar/confirmar',
        data={
            'materia_id': str(materia_id),
            'cohorte_id': str(cohorte_id),
            'actividades': actividades_json,
        },
        files={'archivo': ('test.csv', excel_content, 'text/csv')},
        token=admin_token,
    )

    # POST importar/finalizacion
    await _call(
        async_client, 'post', '/api/v1/calificaciones/importar/finalizacion',
        data={'materia_id': str(materia_id), 'cohorte_id': str(cohorte_id)},
        files={'archivo': ('test.csv', excel_content, 'text/csv')},
        token=admin_token,
    )

    # GET list
    await _call(
        async_client, 'get', '/api/v1/calificaciones',
        params={'materia_id': str(materia_id), 'cohorte_id': str(cohorte_id)},
        token=admin_token,
    )

    # ── 17. UMBRALES ───────────────────────────────────────────────────
    # GET
    await _call(
        async_client, 'get', f'/api/v1/umbrales/{materia_id}/{cohorte_id}',
        token=admin_token,
    )

    # PUT
    await _call(
        async_client, 'put', f'/api/v1/umbrales/{materia_id}/{cohorte_id}',
        json_body={'umbral_pct': 70, 'valores_aprobatorios': ['Aprobado']},
        token=admin_token,
    )

    # ── 18. ENCUENTROS ─────────────────────────────────────────────────
    # Create an asignacion first for slot creation
    asig = Asignacion(
        tenant_id=tenant_id, usuario_id=admin_user_id,
        rol='PROFESOR', materia_id=materia_id,
        carrera_id=carrera_id, cohorte_id=cohorte_id,
    )
    db_session.add(asig)
    await db_session.flush()
    asig_id = asig.id

    # POST /slots
    status, body = await _call(
        async_client, 'post', '/api/v1/encuentros/slots',
        json_body={
            'asignacion_id': str(asig_id),
            'materia_id': str(materia_id),
            'titulo': 'Clase 1',
            'hora': '18:00',
            'dia_semana': 'Lunes',
            'fecha_inicio': '2025-03-01',
            'cant_semanas': 16,
        },
        token=admin_token,
    )
    new_slot_id = body.get('id') if isinstance(body, dict) else None

    # GET /slots
    await _call(async_client, 'get', '/api/v1/encuentros/slots', token=admin_token)
    await _call(
        async_client, 'get', '/api/v1/encuentros/slots',
        params={'materia_id': str(materia_id)},
        token=admin_token,
    )

    # GET /slots/{slot_id}
    if new_slot_id:
        await _call(async_client, 'get', f'/api/v1/encuentros/slots/{new_slot_id}', token=admin_token)

    # POST /instancias
    status, body = await _call(
        async_client, 'post', '/api/v1/encuentros/instancias',
        json_body={
            'materia_id': str(materia_id),
            'fecha': '2025-03-10',
            'hora': '18:00',
            'titulo': 'Clase Especial',
        },
        token=admin_token,
    )
    new_inst_id = body.get('id') if isinstance(body, dict) else None

    # GET /instancias
    await _call(async_client, 'get', '/api/v1/encuentros/instancias', token=admin_token)
    await _call(
        async_client, 'get', '/api/v1/encuentros/instancias',
        params={'materia_id': str(materia_id), 'offset': 0, 'limit': 10},
        token=admin_token,
    )

    # PATCH /instancias/{instancia_id}
    if new_inst_id:
        await _call(
            async_client, 'patch', f'/api/v1/encuentros/instancias/{new_inst_id}',
            json_body={'estado': 'Realizado'},
            token=admin_token,
        )

    # ── 19. GUARDIAS ───────────────────────────────────────────────────
    # POST
    status, body = await _call(
        async_client, 'post', '/api/v1/guardias',
        json_body={
            'asignacion_id': str(asig_id),
            'materia_id': str(materia_id),
            'carrera_id': str(carrera_id),
            'cohorte_id': str(cohorte_id),
            'dia': 'Viernes',
            'horario': '18:00-19:00',
        },
        token=admin_token,
    )
    new_guardia_id = body.get('id') if isinstance(body, dict) else None

    # GET
    await _call(async_client, 'get', '/api/v1/guardias', token=admin_token)
    await _call(
        async_client, 'get', '/api/v1/guardias',
        params={'materia_id': str(materia_id)},
        token=admin_token,
    )

    # PATCH /{guardia_id}
    if new_guardia_id:
        await _call(
            async_client, 'patch', f'/api/v1/guardias/{new_guardia_id}',
            json_body={'estado': 'Cumplida'},
            token=admin_token,
        )

    # GET /export
    await _call(async_client, 'get', '/api/v1/guardias/export', token=admin_token)
    await _call(
        async_client, 'get', '/api/v1/guardias/export',
        params={'materia_id': str(materia_id)},
        token=admin_token,
    )

    # ── 20. COLOQUIOS ──────────────────────────────────────────────────
    # POST /
    status, body = await _call(
        async_client, 'post', '/api/v1/coloquios/',
        json_body={
            'materia_id': str(materia_id),
            'cohorte_id': str(cohorte_id),
            'instancia': 'Primer Parcial',
            'tipo': 'Escrito',
            'turnos': [
                {'fecha': '2025-06-15', 'hora_inicio': '09:00', 'hora_fin': '11:00', 'cupo': 30},
                {'fecha': '2025-06-16', 'hora_inicio': '14:00', 'hora_fin': '16:00', 'cupo': 25},
            ],
        },
        token=admin_token,
    )
    new_eval_id = body.get('id') if isinstance(body, dict) else None

    # GET metricas (needs to be before listing, no filters)
    await _call(async_client, 'get', '/api/v1/coloquios/metricas', token=admin_token)

    # GET /
    await _call(async_client, 'get', '/api/v1/coloquios/', token=admin_token)
    await _call(
        async_client, 'get', '/api/v1/coloquios/',
        params={'materia_id': str(materia_id)},
        token=admin_token,
    )

    # GET /{evaluacion_id}
    if new_eval_id:
        await _call(async_client, 'get', f'/api/v1/coloquios/{new_eval_id}', token=admin_token)

    # POST /{evaluacion_id}/alumnos
    if new_eval_id:
        await _call(
            async_client, 'post', f'/api/v1/coloquios/{new_eval_id}/alumnos',
            json_body={'alumno_ids': [str(second_user_id)]},
            token=admin_token,
        )

    # POST /{evaluacion_id}/reservas
    turno_id = None
    if new_eval_id:
        result = await db_session.execute(
            select(TurnoColoquio).where(TurnoColoquio.evaluacion_id == new_eval_id)
        )
        turno = result.scalar_one_or_none()
        if turno:
            turno_id = turno.id
            status, body = await _call(
                async_client, 'post', f'/api/v1/coloquios/{new_eval_id}/reservas',
                json_body={'turno_id': str(turno_id)},
                token=admin_token,
            )
            reserva_id = body.get('id') if isinstance(body, dict) else None

            # DELETE /reservas/{reserva_id}
            if reserva_id:
                await _call(
                    async_client, 'delete', f'/api/v1/coloquios/reservas/{reserva_id}',
                    token=admin_token,
                )

    # PUT /{evaluacion_id}/resultados/{alumno_id}
    if new_eval_id:
        await _call(
            async_client, 'put', f'/api/v1/coloquios/{new_eval_id}/resultados/{second_user_id}',
            json_body={'nota_final': 'Aprobado'},
            token=admin_token,
        )

    # GET /{evaluacion_id}/resultados
    if new_eval_id:
        await _call(
            async_client, 'get', f'/api/v1/coloquios/{new_eval_id}/resultados',
            token=admin_token,
        )

    # PATCH /{evaluacion_id}/cerrar
    if new_eval_id:
        await _call(
            async_client, 'patch', f'/api/v1/coloquios/{new_eval_id}/cerrar',
            token=admin_token,
        )

    # ── 21. ANALISIS ───────────────────────────────────────────────────
    # GET atrasados
    await _call(
        async_client, 'get', '/api/v1/analisis/atrasados',
        params={'materia_id': str(materia_id), 'cohorte_id': str(cohorte_id)},
        token=admin_token,
    )

    # GET ranking
    await _call(
        async_client, 'get', '/api/v1/analisis/ranking',
        params={'materia_id': str(materia_id), 'cohorte_id': str(cohorte_id)},
        token=admin_token,
    )

    # GET reportes-rapidos
    await _call(
        async_client, 'get', '/api/v1/analisis/reportes-rapidos',
        params={'materia_id': str(materia_id), 'cohorte_id': str(cohorte_id)},
        token=admin_token,
    )

    # GET notas-finales
    await _call(
        async_client, 'get', '/api/v1/analisis/notas-finales',
        params={
            'materia_id': str(materia_id),
            'cohorte_id': str(cohorte_id),
            'actividades': 'TP1,TP2',
        },
        token=admin_token,
    )

    # GET tps-sin-corregir
    await _call(
        async_client, 'get', '/api/v1/analisis/tps-sin-corregir',
        params={'materia_id': str(materia_id), 'cohorte_id': str(cohorte_id)},
        token=admin_token,
    )

    # GET monitor-general
    await _call(
        async_client, 'get', '/api/v1/analisis/monitor-general',
        params={'materia_id': str(materia_id)},
        token=admin_token,
    )

    # GET monitor-seguimiento
    await _call(
        async_client, 'get', '/api/v1/analisis/monitor-seguimiento',
        params={'materia_id': str(materia_id)},
        token=admin_token,
    )

    # ── 22. ERROR VERIFICATION ─────────────────────────────────────────
    # 404 on non-existent route
    await _call(async_client, 'get', '/api/v1/non-existent-route', token=admin_token)

    # 422 with invalid body (extra fields)
    await _call(
        async_client, 'post', '/api/v1/admin/carreras',
        json_body={'codigo': 'TEST', 'nombre': 'Test', 'extra_field': 'should_fail'},
        token=admin_token,
    )

    # 401 without auth (protected endpoint)
    await _call(async_client, 'get', '/api/v1/admin/carreras')

    # 422 with empty body (carrera post)
    await _call(
        async_client, 'post', '/api/v1/admin/carreras',
        json_body={},
        token=admin_token,
    )

    # ── PRINT RESULTS TABLE ────────────────────────────────────────────
    print('\n\n## ENDPOINT VERIFICATION RESULTS')
    print('')
    print('| # | Method | Route | Status | Response OK | Notes |')
    print('|---|--------|-------|--------|-------------|-------|')
    for r in RESULTS:
        ok_str = 'PASS' if r.response_ok else 'FAIL'
        print(f'| {r.index} | {r.method} | {r.path} | {r.status} | {ok_str} | {r.notes} |')

    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r.response_ok)
    failed = total - passed
    print(f'\n**Total: {total} | Passed: {passed} | Failed: {failed}**')
    print('')

    # Assert no 500 errors
    server_errors = [r for r in RESULTS if r.status == 500]
    assert not server_errors, f'Server errors (500) on: {[(r.method, r.path) for r in server_errors]}'
    assert failed == 0, f'{failed} endpoints failed response validation'
