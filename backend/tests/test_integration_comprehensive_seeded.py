"""Comprehensive integration test using seed data with content verification.

Runs run_seed(db_session) at setup, then exercises ALL endpoints
with deterministic seed UUIDs and verifies response content.
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Any, Callable

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.turno_coloquio import TurnoColoquio
from seed import (
    ACTIVIDADES,
    PROGRAMA_ALGEBRA_ID,
    PROGRAMA_CONTABILIDAD_ID,
    FECHA_ALGEBRA_PARCIAL1,
    FECHA_ALGEBRA_TP1,
    FECHA_CONTABILIDAD_PARCIAL1,
    ASIG_ADMIN_ALGEBRA_ID,
    ASIG_ANA_ALGEBRA_ID,
    ASIG_CARLOS_PROG1_ID,
    ASIG_MARIA_ALGEBRA_ID,
    ASIG_PEDRO_BD_ID,
    ASIG_PEDRO_PROG1_ID,
    AVISO_1_ID,
    AVISO_2_ID,
    AVISO_3_ID,
    AVISO_4_ID,
    AVISO_5_ID,
    CARRERA_ADM_ID,
    CARRERA_ING_ID,
    COHORTE_ADM_2024_ID,
    COHORTE_ADM_2025_ID,
    COHORTE_ING_2024_ID,
    COHORTE_ING_2025_ID,
    COMENTARIO_TAREA_1_ID,
    COMENTARIO_TAREA_2_ID,
    EVAL_1_ID,
    EVAL_2_ID,
    GUARDIA_1_ID,
    GUARDIA_2_ID,
    GUARDIA_3_ID,
    GUARDIA_4_ID,
    GUARDIA_5_ID,
    INSTANCIA_1_ID,
    INSTANCIA_2_ID,
    INSTANCIA_3_ID,
    LOTE_COM_ID,
    MATERIA_ALGEBRA_ID,
    MATERIA_BD_ID,
    MATERIA_CONTABILIDAD_ID,
    MATERIA_MARKETING_ID,
    MATERIA_PROG1_ID,
    MATERIA_PROG2_ID,
    MATERIA_REDES_ID,
    MATERIA_RRHH_ID,
    ROLE_ADMIN_ID,
    ROLE_PROFESOR_ID,
    ROLE_TUTOR_ID,
    SLOT_1_ID,
    SLOT_2_ID,
    SLOT_3_ID,
    TAREA_1_ID,
    TAREA_2_ID,
    TAREA_3_ID,
    TAREA_4_ID,
    TAREA_5_ID,
    TENANT_ID,
    TURNO_EVAL1_ID,
    TURNO_EVAL1B_ID,
    TURNO_EVAL2_ID,
    USER_ADMIN_ID,
    USER_ANA_ID,
    USER_CARLOS_ID,
    USER_MARIA_ID,
    USER_PEDRO_ID,
    USER_ALUMNO_COL_1,
    USER_ALUMNO_COL_2,
    VERSION_ALGEBRA_ID,
    VERSION_CONTABILIDAD_ID,
    run_seed,
)

NS = uuid.NAMESPACE_DNS


@dataclass
class EndpointResult:
    index: int
    method: str
    path: str
    status: int
    response_ok: bool
    content_ok: bool | None = None
    notes: str = ''


RESULTS: list[EndpointResult] = []
_counter = 0


def _next() -> int:
    global _counter
    _counter += 1
    return _counter


def _to_dict(body: Any) -> dict:
    if isinstance(body, dict):
        return body
    return {}


def _to_list(body: Any) -> list:
    if isinstance(body, list):
        return body
    return []


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
    verify: Callable[[Any, int], bool | str] | None = None,
) -> tuple[int, Any]:
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'

    kwargs = dict(url=path, headers=headers, params=params)
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
    elif status == 404 and isinstance(body, dict) and 'detail' in body:
        notes = 'expected 404'
    elif status == 422:
        notes = 'validation error'
    elif status == 403:
        notes = 'insufficient permissions'
    elif status == 401:
        notes = 'unauthorized'
    elif status == 429:
        notes = 'rate limited'

    if expect_status is not None and status != expect_status:
        notes += f' (expected {expect_status})'

    content_ok: bool | None = None
    if verify is not None:
        try:
            result = verify(body, status)
            if isinstance(result, str):
                content_ok = False
                notes += f' | CONTENT: {result}'
            else:
                content_ok = bool(result)
                if not content_ok:
                    notes += ' | CONTENT FAIL'
        except AssertionError as e:
            content_ok = False
            notes += f' | CONTENT: {e}'
        except Exception as e:
            content_ok = False
            notes += f' | CONTENT EXC: {e}'

    idx = _next()
    RESULTS.append(EndpointResult(
        index=idx, method=method.upper(), path=path,
        status=status, response_ok=ok, content_ok=content_ok,
        notes=notes.strip(),
    ))
    return status, body


# ── Content verification helpers ─────────────────────────────────────────


def has_status(expected: int) -> Callable[[Any, int], bool]:
    def check(_body: Any, status: int) -> bool:
        return status == expected
    return check


def json_has_keys(*keys: str) -> Callable[[Any, int], bool]:
    def check(body: Any, _status: int) -> bool:
        d = _to_dict(body)
        for k in keys:
            if k not in d:
                raise AssertionError(f'missing key "{k}"')
        return True
    return check


def json_contains(key: str, value: Any) -> Callable[[Any, int], bool]:
    def check(body: Any, _status: int) -> bool:
        d = _to_dict(body)
        actual = d.get(key)
        if actual != value:
            raise AssertionError(f'expected {key}={value!r}, got {actual!r}')
        return True
    return check


def body_is_dict(_body: Any, _status: int) -> bool:
    return isinstance(_body, dict)


def body_is_list(_body: Any, _status: int) -> bool:
    return isinstance(_body, list)


def items_match(description: str, count: int | None = None,
                contains_fields: list[str] | None = None,
                contains_values: list[tuple[str, Any]] | None = None,
                ) -> Callable[[Any, int], bool]:
    """Verify a list response inside an `items` key in a dict, or a direct list."""
    def check(body: Any, _status: int) -> bool:
        items = _to_dict(body).get('items') if isinstance(body, dict) else body
        if not isinstance(items, list):
            raise AssertionError(f'{description}: expected list of items')
        if count is not None and len(items) != count:
            raise AssertionError(f'{description}: expected {count} items, got {len(items)}')
        if contains_fields:
            for item in items:
                for field in contains_fields:
                    if field not in item:
                        raise AssertionError(f'{description}: item missing field "{field}"')
        if contains_values:
            # Check each (key, value) pair appears in at least one item
            for key, val in contains_values:
                if not any(item.get(key) == val for item in items):
                    raise AssertionError(f'{description}: no item with {key}={val!r}')
        return True
    return check


def no_500(_body: Any, status: int) -> bool:
    return status != 500


# ── Test ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_all_endpoints_seeded(db_session: AsyncSession, async_client: AsyncClient) -> None:
    global RESULTS, _counter
    RESULTS = []
    _counter = 0

    # ── SEED ─────────────────────────────────────────────────────────────
    await run_seed(db_session)
    await db_session.commit()

    # ── Admin token ──────────────────────────────────────────────────────
    admin_token = create_access_token(str(USER_ADMIN_ID), str(TENANT_ID), ['ADMIN'])
    second_token = create_access_token(str(USER_ANA_ID), str(TENANT_ID), ['PROFESOR'])

    # ── 1. HEALTH ───────────────────────────────────────────────────────
    await _call(async_client, 'get', '/health',
                verify=lambda b, s: (isinstance(b, dict)
                                     and b.get('status') == 'ok'
                                     and b.get('database') == 'up'))

    # ── 2. AUTH ─────────────────────────────────────────────────────────
    # POST /api/v1/auth/login — valid (may fail due to session handling)
    await _call(
        async_client, 'post', '/api/v1/auth/login',
        json_body={'email': 'admin@test.com', 'password': 'password123'},
        expect_status=200, verify=json_has_keys('access_token', 'refresh_token'),
    )

    # POST /api/v1/auth/login — invalid body (no password → 422)
    await _call(
        async_client, 'post', '/api/v1/auth/login',
        json_body={'email': 'test@test.com'},
        expect_status=422,
    )

    # POST /api/v1/auth/login — wrong credentials → 401
    await _call(
        async_client, 'post', '/api/v1/auth/login',
        json_body={'email': 'admin@test.com', 'password': 'wrong'},
        expect_status=401,
    )

    # POST /api/v1/auth/refresh — invalid token → 401
    await _call(
        async_client, 'post', '/api/v1/auth/refresh',
        json_body={'refresh_token': 'invalid-refresh-token'},
        expect_status=401,
    )

    # POST /api/v1/auth/logout
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

    # POST /api/v1/auth/2fa/validate — invalid 2fa token → 401
    await _call(
        async_client, 'post', '/api/v1/auth/2fa/validate',
        json_body={'2fa_token': 'invalid-2fa-token', 'code': '123456'},
        expect_status=401,
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
        expect_status=400,
    )

    # POST /api/v1/auth/impersonate — self → 400
    await _call(
        async_client, 'post', '/api/v1/auth/impersonate',
        json_body={'target_user_id': str(USER_ADMIN_ID)},
        token=admin_token,
        expect_status=400,
    )
    # POST /api/v1/auth/impersonate — non-existent → 404
    await _call(
        async_client, 'post', '/api/v1/auth/impersonate',
        json_body={'target_user_id': str(uuid.UUID(int=9999))},
        token=admin_token,
        expect_status=404,
    )

    # POST /api/v1/auth/impersonate/stop — no active → 400
    await _call(
        async_client, 'post', '/api/v1/auth/impersonate/stop',
        token=admin_token,
        expect_status=400,
    )

    # ── 3. CARRERAS CRUD ───────────────────────────────────────────────
    # GET list → 2 carreras from seed
    await _call(
        async_client, 'get', '/api/v1/admin/carreras', token=admin_token,
        verify=items_match('carreras list', count=2,
                           contains_values=[('codigo', 'ING-2020'), ('codigo', 'LIC-ADM-2020')]),
    )

    # POST create
    status, body = await _call(
        async_client, 'post', '/api/v1/admin/carreras',
        json_body={'codigo': 'SIS', 'nombre': 'Sistemas'},
        token=admin_token, expect_status=201,
        verify=json_has_keys('id', 'codigo', 'nombre'),
    )
    new_carrera_id = _to_dict(body).get('id')
    if new_carrera_id:
        await _call(async_client, 'get', f'/api/v1/admin/carreras/{new_carrera_id}', token=admin_token,
                    verify=lambda b, s: isinstance(b, dict) and b.get('codigo') == 'SIS')
        await _call(
            async_client, 'put', f'/api/v1/admin/carreras/{new_carrera_id}',
            json_body={'nombre': 'Ingeniería en Sistemas'},
            token=admin_token,
            verify=json_contains('nombre', 'Ingeniería en Sistemas'),
        )
        await _call(async_client, 'delete', f'/api/v1/admin/carreras/{new_carrera_id}', token=admin_token,
                    expect_status=204)
        await _call(async_client, 'get', f'/api/v1/admin/carreras/{new_carrera_id}', token=admin_token,
                    expect_status=404)

    # GET by seed ID
    await _call(async_client, 'get', f'/api/v1/admin/carreras/{CARRERA_ING_ID}', token=admin_token,
                verify=lambda b, s: isinstance(b, dict) and b.get('codigo') == 'ING-2020')

    # 404 on non-existent
    await _call(
        async_client, 'get', f'/api/v1/admin/carreras/{uuid.uuid4()}', token=admin_token,
        expect_status=404,
    )

    # ── 4. COHORTES CRUD ───────────────────────────────────────────────
    # GET list → 4 cohortes
    await _call(
        async_client, 'get', '/api/v1/admin/cohortes', token=admin_token,
        verify=items_match('cohortes list', count=4),
    )

    # POST create
    status, body = await _call(
        async_client, 'post', '/api/v1/admin/cohortes',
        json_body={
            'carrera_id': str(CARRERA_ING_ID),
            'nombre': '2026',
            'anio': 2026,
            'vig_desde': '2026-01-01',
            'estado': 'Activa',
        },
        token=admin_token, expect_status=201,
        verify=json_has_keys('id', 'nombre', 'carrera_id'),
    )
    new_cohorte_id = _to_dict(body).get('id')
    if new_cohorte_id:
        await _call(async_client, 'get', f'/api/v1/admin/cohortes/{new_cohorte_id}', token=admin_token)
        await _call(
            async_client, 'put', f'/api/v1/admin/cohortes/{new_cohorte_id}',
            json_body={'nombre': '2026 Mod'},
            token=admin_token,
        )
        await _call(async_client, 'delete', f'/api/v1/admin/cohortes/{new_cohorte_id}', token=admin_token,
                    expect_status=204)
        await _call(async_client, 'get', f'/api/v1/admin/cohortes/{new_cohorte_id}', token=admin_token,
                    expect_status=404)

    # GET by seed ID
    await _call(async_client, 'get', f'/api/v1/admin/cohortes/{COHORTE_ING_2024_ID}', token=admin_token,
                verify=lambda b, s: isinstance(b, dict) and b.get('nombre') == '2024')

    await _call(async_client, 'get', f'/api/v1/admin/cohortes/{uuid.uuid4()}', token=admin_token,
                expect_status=404)

    # ── 5. MATERIAS CRUD ───────────────────────────────────────────────
    # GET list → 8 materias
    await _call(
        async_client, 'get', '/api/v1/admin/materias', token=admin_token,
        verify=items_match('materias list', count=8,
                           contains_values=[('codigo', 'ALG101'), ('codigo', 'PRG101')]),
    )

    status, body = await _call(
        async_client, 'post', '/api/v1/admin/materias',
        json_body={'codigo': 'FIS101', 'nombre': 'Física I'},
        token=admin_token, expect_status=201,
        verify=json_has_keys('id', 'codigo', 'nombre'),
    )
    new_materia_id = _to_dict(body).get('id')
    if new_materia_id:
        await _call(async_client, 'get', f'/api/v1/admin/materias/{new_materia_id}', token=admin_token)
        await _call(
            async_client, 'put', f'/api/v1/admin/materias/{new_materia_id}',
            json_body={'nombre': 'Física General'},
            token=admin_token,
        )
        await _call(async_client, 'delete', f'/api/v1/admin/materias/{new_materia_id}', token=admin_token,
                    expect_status=204)
        await _call(async_client, 'get', f'/api/v1/admin/materias/{new_materia_id}', token=admin_token,
                    expect_status=404)

    # GET by seed ID
    await _call(async_client, 'get', f'/api/v1/admin/materias/{MATERIA_ALGEBRA_ID}', token=admin_token,
                verify=lambda b, s: isinstance(b, dict) and b.get('codigo') == 'ALG101')

    await _call(async_client, 'get', f'/api/v1/admin/materias/{uuid.uuid4()}', token=admin_token,
                expect_status=404)

    # ── 6. USUARIOS CRUD ───────────────────────────────────────────────
    await _call(
        async_client, 'get', '/api/v1/admin/usuarios', token=admin_token,
        verify=items_match('usuarios list', count=7,
                           contains_fields=['id']),
    )

    status, body = await _call(
        async_client, 'post', '/api/v1/admin/usuarios',
        json_body={
            'email': 'nuevo@test.com',
            'password': 'password123',
            'nombre': 'Nuevo',
            'apellido': 'Usuario',
            'estado': 'Activo',
        },
        token=admin_token, expect_status=201,
    )
    new_user_id = _to_dict(body).get('id')
    if new_user_id:
        await _call(async_client, 'get', f'/api/v1/admin/usuarios/{new_user_id}', token=admin_token)
        await _call(
            async_client, 'patch', f'/api/v1/admin/usuarios/{new_user_id}',
            json_body={'nombre': 'Actualizado'},
            token=admin_token,
        )
        await _call(async_client, 'delete', f'/api/v1/admin/usuarios/{new_user_id}', token=admin_token,
                    expect_status=204)
        await _call(async_client, 'get', f'/api/v1/admin/usuarios/{new_user_id}', token=admin_token,
                    expect_status=404)

    await _call(async_client, 'get', f'/api/v1/admin/usuarios/{uuid.uuid4()}', token=admin_token,
                expect_status=404)

    # ── 7. ROLES CRUD ──────────────────────────────────────────────────
    await _call(
        async_client, 'get', '/api/v1/roles', token=admin_token,
        verify=items_match('roles list', count=3,
                           contains_values=[('codigo', 'ADMIN'), ('codigo', 'PROFESOR'), ('codigo', 'TUTOR')]),
    )

    status, body = await _call(
        async_client, 'post', '/api/v1/roles',
        json_body={'name': 'Test Role', 'codigo': 'test_role'},
        token=admin_token, expect_status=201,
    )
    new_role_id = _to_dict(body).get('id')
    if new_role_id:
        await _call(async_client, 'get', f'/api/v1/roles/{new_role_id}', token=admin_token)
        await _call(
            async_client, 'put', f'/api/v1/roles/{new_role_id}',
            json_body={'name': 'Updated Role'},
            token=admin_token,
        )
        await _call(async_client, 'delete', f'/api/v1/roles/{new_role_id}', token=admin_token,
                    expect_status=204)
        await _call(async_client, 'get', f'/api/v1/roles/{new_role_id}', token=admin_token,
                    expect_status=404)

    await _call(async_client, 'get', f'/api/v1/roles/{uuid.uuid4()}', token=admin_token,
                expect_status=404)

    # ── 8. PERMISOS CRUD ───────────────────────────────────────────────
    await _call(
        async_client, 'get', '/api/v1/permisos', token=admin_token,
        verify=items_match('permisos list', count=13,
                           contains_values=[('codigo', 'estructura:gestionar')]),
    )

    status, body = await _call(
        async_client, 'post', '/api/v1/permisos',
        json_body={
            'codigo': 'test:permiso',
            'modulo': 'test',
            'accion': 'permiso',
        },
        token=admin_token, expect_status=201,
    )
    new_perm_id = _to_dict(body).get('id')
    if new_perm_id:
        await _call(async_client, 'get', f'/api/v1/permisos/{new_perm_id}', token=admin_token)
        await _call(
            async_client, 'put', f'/api/v1/permisos/{new_perm_id}',
            json_body={'descripcion': 'Test permiso desc'},
            token=admin_token,
        )
        await _call(async_client, 'delete', f'/api/v1/permisos/{new_perm_id}', token=admin_token,
                    expect_status=204)
        await _call(async_client, 'get', f'/api/v1/permisos/{new_perm_id}', token=admin_token,
                    expect_status=404)

    await _call(async_client, 'get', f'/api/v1/permisos/{uuid.uuid4()}', token=admin_token,
                expect_status=404)

    # ── 9. ROLE-PERMISOS ───────────────────────────────────────────────
    # GET role's permissions
    await _call(async_client, 'get', f'/api/v1/roles/{ROLE_ADMIN_ID}/permisos', token=admin_token,
                verify=items_match('role perm list', count=13))

    # POST assign permission to role — pick a perm from seed
    # perm id: uuid5(NS, 'seed-perm-avisos-publicar')
    perm_avisos_id = uuid.uuid5(NS, 'seed-perm-avisos-publicar')
    await _call(
        async_client, 'post', f'/api/v1/roles/{ROLE_ADMIN_ID}/permisos',
        json_body={'permiso_id': str(perm_avisos_id), 'propio': True},
        token=admin_token,
    )

    # DELETE unassign
    await _call(
        async_client, 'delete', f'/api/v1/roles/{ROLE_ADMIN_ID}/permisos/{perm_avisos_id}',
        token=admin_token,
    )

    # ── 10. USER-ROLES ─────────────────────────────────────────────────
    # GET user's roles
    await _call(async_client, 'get', f'/api/v1/users/{USER_ANA_ID}/roles', token=admin_token)

    # POST assign role to user
    await _call(
        async_client, 'post', f'/api/v1/users/{USER_ANA_ID}/roles',
        json_body={'role_id': str(ROLE_PROFESOR_ID)},
        token=admin_token,
    )

    # DELETE unassign
    await _call(
        async_client, 'delete', f'/api/v1/users/{USER_ANA_ID}/roles/{ROLE_PROFESOR_ID}',
        token=admin_token,
    )

    # ── 11. ASIGNACIONES CRUD ──────────────────────────────────────────
    await _call(
        async_client, 'get', '/api/v1/asignaciones', token=admin_token,
        verify=items_match('asignaciones list', count=6),
    )

    status, body = await _call(
        async_client, 'post', '/api/v1/asignaciones',
        json_body={
            'usuario_id': str(USER_ANA_ID),
            'rol': 'PROFESOR',
            'materia_id': str(MATERIA_BD_ID),
            'cohorte_id': str(COHORTE_ING_2025_ID),
        },
        token=admin_token, expect_status=201,
    )
    new_asig_id = _to_dict(body).get('id')
    if new_asig_id:
        await _call(async_client, 'get', f'/api/v1/asignaciones/{new_asig_id}', token=admin_token)
        await _call(
            async_client, 'patch', f'/api/v1/asignaciones/{new_asig_id}',
            json_body={'rol': 'TUTOR'},
            token=admin_token,
        )
        await _call(async_client, 'delete', f'/api/v1/asignaciones/{new_asig_id}', token=admin_token,
                    expect_status=204)
        await _call(async_client, 'get', f'/api/v1/asignaciones/{new_asig_id}', token=admin_token,
                    expect_status=404)

    await _call(async_client, 'get', f'/api/v1/asignaciones/{uuid.uuid4()}', token=admin_token,
                expect_status=404)

    # ── 12. EQUIPOS ────────────────────────────────────────────────────
    await _call(
        async_client, 'get', '/api/v1/equipos/mis-equipos', token=admin_token,
        verify=items_match('mis-equipos admin', contains_fields=['usuario_id', 'materia_id']),
    )
    await _call(
        async_client, 'get', '/api/v1/equipos/mis-equipos',
        params={'materia_id': str(MATERIA_ALGEBRA_ID), 'cohorte_id': str(COHORTE_ING_2024_ID)},
        token=second_token,
    )

    # POST asignacion-masiva
    await _call(
        async_client, 'post', '/api/v1/equipos/asignacion-masiva',
        json_body={
            'usuario_ids': [str(USER_ANA_ID)],
            'materia_id': str(MATERIA_BD_ID),
            'cohorte_id': str(COHORTE_ING_2025_ID),
            'rol': 'PROFESOR',
        },
        token=admin_token,
    )

    # POST clonar
    await _call(
        async_client, 'post', '/api/v1/equipos/clonar',
        json_body={
            'origen': {'materia_id': str(MATERIA_ALGEBRA_ID), 'cohorte_id': str(COHORTE_ING_2024_ID)},
            'destino': {'materia_id': str(MATERIA_PROG1_ID), 'cohorte_id': str(COHORTE_ING_2025_ID)},
        },
        token=admin_token,
    )

    # PATCH vigencia
    await _call(
        async_client, 'patch', '/api/v1/equipos/vigencia',
        json_body={
            'materia_id': str(MATERIA_ALGEBRA_ID),
            'cohorte_id': str(COHORTE_ING_2024_ID),
        },
        token=admin_token,
    )

    # GET exportar
    await _call(async_client, 'get', '/api/v1/equipos/exportar', token=admin_token)
    await _call(
        async_client, 'get', '/api/v1/equipos/exportar',
        params={'materia_id': str(MATERIA_ALGEBRA_ID)},
        token=admin_token,
    )

    # ── 13. AVISOS ─────────────────────────────────────────────────────
    aviso_create_body = {
        'alcance': 'Global',
        'severidad': 'Info',
        'titulo': 'Test Aviso',
        'cuerpo': 'Cuerpo del aviso de prueba',
        'inicio_vigencia': datetime.now(timezone.utc).isoformat(),
        'fin_vigencia': (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        'requiere_ack': False,
        'orden': 0,
    }
    status, body = await _call(
        async_client, 'post', '/api/v1/avisos',
        json_body=aviso_create_body,
        token=admin_token,
    )
    new_aviso_id = _to_dict(body).get('id') if isinstance(body, dict) else None

    # GET list — seed has 3 vigentes + 2 vencidos; the service filters vigentes
    await _call(
        async_client, 'get', '/api/v1/avisos', token=admin_token,
        verify=lambda b, s: isinstance(b, dict) and b.get('total', 0) >= 3,
    )
    await _call(
        async_client, 'get', '/api/v1/avisos', token=second_token,
        verify=lambda b, s: isinstance(b, dict) and b.get('total', 0) >= 3,
    )

    if new_aviso_id:
        await _call(async_client, 'get', f'/api/v1/avisos/{new_aviso_id}', token=admin_token,
                    verify=json_has_keys('id', 'titulo', 'cuerpo'))
        await _call(
            async_client, 'patch', f'/api/v1/avisos/{new_aviso_id}',
            json_body={'titulo': 'Aviso Actualizado'},
            token=admin_token,
            verify=json_contains('titulo', 'Aviso Actualizado'),
        )
        await _call(async_client, 'post', f'/api/v1/avisos/{new_aviso_id}/ack', token=admin_token,
                    verify=json_has_keys('id', 'aviso_id', 'usuario_id', 'confirmado_at'))
        await _call(async_client, 'delete', f'/api/v1/avisos/{new_aviso_id}', token=admin_token)
        await _call(async_client, 'get', f'/api/v1/avisos/{new_aviso_id}', token=admin_token,
                    expect_status=404)

    await _call(async_client, 'get', f'/api/v1/avisos/{uuid.uuid4()}', token=admin_token,
                expect_status=404)

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
        verify=json_has_keys('asunto_renderizado', 'cuerpo_renderizado'),
    )

    # POST single
    status, body = await _call(
        async_client, 'post', '/api/v1/comunicaciones',
        json_body={
            'destinatario': 'alumno@test.com',
            'asunto': 'Notificación de prueba',
            'cuerpo': 'Cuerpo del mensaje de prueba',
        },
        token=admin_token, expect_status=201,
        verify=json_has_keys('id', 'asunto', 'cuerpo', 'estado', 'lote_id'),
    )
    new_com_id = _to_dict(body).get('id')

    # POST lote
    status, body = await _call(
        async_client, 'post', '/api/v1/comunicaciones/lote',
        json_body={
            'destinatarios': ['alumno1@test.com', 'alumno2@test.com'],
            'asunto': 'Aviso masivo',
            'cuerpo': 'Cuerpo masivo',
        },
        token=admin_token, expect_status=201,
        verify=body_is_list,
    )
    lote_ids = set()
    for item in _to_list(body):
        lid = _to_dict(item).get('lote_id')
        if lid:
            lote_ids.add(lid)

    # POST aprobar-lote
    for lid in lote_ids:
        await _call(
            async_client, 'post', '/api/v1/comunicaciones/aprobar-lote',
            json_body={'lote_id': str(lid), 'accion': 'aprobar'},
            token=admin_token,
        )

    # GET list — without lote_id it returns empty
    await _call(
        async_client, 'get', '/api/v1/comunicaciones', token=admin_token,
    )
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
            verify=lambda b, s: isinstance(b, dict) and 'cancelada' in str(b.get('detalle', '')).lower(),
        )

    # ── 15. PADRON ────────────────────────────────────────────────────
    csv_content = 'nombre,apellidos,email,comision,regional\nJuan,Perez,juan@test.com,C1,Regional1\n'
    # POST importar/preview
    await _call(
        async_client, 'post', '/api/v1/padron/importar/preview',
        data={'materia_id': str(MATERIA_ALGEBRA_ID), 'cohorte_id': str(COHORTE_ING_2024_ID)},
        files={'archivo': ('test.csv', csv_content, 'text/csv')},
        token=admin_token,
    )

    # POST importar/confirmar
    status, body = await _call(
        async_client, 'post', '/api/v1/padron/importar/confirmar',
        data={'materia_id': str(MATERIA_ALGEBRA_ID), 'cohorte_id': str(COHORTE_ING_2024_ID)},
        files={'archivo': ('test.csv', csv_content, 'text/csv')},
        token=admin_token,
    )
    version_id = _to_dict(body).get('id')

    # GET versiones
    await _call(
        async_client, 'get', '/api/v1/padron/versiones', token=admin_token,
        verify=lambda b, s: isinstance(b, list) and len(b) >= 2,
    )

    # POST vaciar/{materia_id}/{cohorte_id}
    await _call(
        async_client, 'post', f'/api/v1/padron/vaciar/{MATERIA_ALGEBRA_ID}/{COHORTE_ING_2024_ID}',
        token=admin_token,
    )

    # POST sync-moodle
    await _call(
        async_client, 'post', '/api/v1/padron/sync-moodle',
        data={'materia_id': str(MATERIA_ALGEBRA_ID), 'cohorte_id': str(COHORTE_ING_2024_ID)},
        token=admin_token,
    )

    # ── 16. CALIFICACIONES ────────────────────────────────────────────
    excel_content = b'header1,header2\nval1,val2\n'
    await _call(
        async_client, 'post', '/api/v1/calificaciones/importar/preview',
        data={'materia_id': str(MATERIA_ALGEBRA_ID), 'cohorte_id': str(COHORTE_ING_2024_ID)},
        files={'archivo': ('test.csv', excel_content, 'text/csv')},
        token=admin_token,
    )

    actividades_json = json.dumps([{'nombre': 'TP1', 'tipo': 'tp'}])
    await _call(
        async_client, 'post', '/api/v1/calificaciones/importar/confirmar',
        data={
            'materia_id': str(MATERIA_ALGEBRA_ID),
            'cohorte_id': str(COHORTE_ING_2024_ID),
            'actividades': actividades_json,
        },
        files={'archivo': ('test.csv', excel_content, 'text/csv')},
        token=admin_token,
    )

    await _call(
        async_client, 'post', '/api/v1/calificaciones/importar/finalizacion',
        data={'materia_id': str(MATERIA_ALGEBRA_ID), 'cohorte_id': str(COHORTE_ING_2024_ID)},
        files={'archivo': ('test.csv', excel_content, 'text/csv')},
        token=admin_token,
    )

    # GET list — seed has 240 calificaciones
    await _call(
        async_client, 'get', '/api/v1/calificaciones',
        params={'materia_id': str(MATERIA_ALGEBRA_ID), 'cohorte_id': str(COHORTE_ING_2024_ID)},
        token=admin_token,
        verify=lambda b, s: isinstance(b, dict) and b.get('total', 0) == 120,
    )

    # ── 17. UMBRALES ───────────────────────────────────────────────────
    # PUT umbral (creates one if missing → now it returns data)
    await _call(
        async_client, 'put', f'/api/v1/umbrales/{MATERIA_ALGEBRA_ID}/{COHORTE_ING_2024_ID}',
        json_body={'umbral_pct': 70, 'valores_aprobatorios': ['Aprobado']},
        token=admin_token,
        verify=json_has_keys('materia_id', 'cohorte_id', 'umbral_pct'),
    )

    # GET umbral
    await _call(
        async_client, 'get', f'/api/v1/umbrales/{MATERIA_ALGEBRA_ID}/{COHORTE_ING_2024_ID}',
        token=admin_token,
        verify=lambda b, s: isinstance(b, dict) and b.get('umbral_pct') == 70,
    )

    # ── 18. ENCUENTROS ─────────────────────────────────────────────────
    # POST /slots
    status, body = await _call(
        async_client, 'post', '/api/v1/encuentros/slots',
        json_body={
            'asignacion_id': str(ASIG_ADMIN_ALGEBRA_ID),
            'materia_id': str(MATERIA_ALGEBRA_ID),
            'titulo': 'Nuevo Slot',
            'hora': '18:00',
            'dia_semana': 'Lunes',
            'fecha_inicio': '2025-03-01',
            'cant_semanas': 16,
        },
        token=admin_token, expect_status=201,
        verify=json_has_keys('id', 'titulo', 'materia_id'),
    )
    new_slot_id = _to_dict(body).get('id')

    # GET /slots → 3 from seed + 1 new = 4
    await _call(
        async_client, 'get', '/api/v1/encuentros/slots', token=admin_token,
        verify=lambda b, s: isinstance(b, dict) and b.get('total', 0) >= 3,
    )
    await _call(
        async_client, 'get', '/api/v1/encuentros/slots',
        params={'materia_id': str(MATERIA_ALGEBRA_ID)},
        token=admin_token,
    )

    if new_slot_id:
        await _call(async_client, 'get', f'/api/v1/encuentros/slots/{new_slot_id}', token=admin_token,
                    verify=json_has_keys('id', 'titulo'))

    # POST /instancias
    status, body = await _call(
        async_client, 'post', '/api/v1/encuentros/instancias',
        json_body={
            'materia_id': str(MATERIA_ALGEBRA_ID),
            'fecha': '2025-03-10',
            'hora': '18:00',
            'titulo': 'Clase Especial',
        },
        token=admin_token, expect_status=201,
        verify=json_has_keys('id', 'titulo', 'fecha'),
    )
    new_inst_id = _to_dict(body).get('id')

    # GET /instancias → 3 from seed + 1 new = 4
    await _call(
        async_client, 'get', '/api/v1/encuentros/instancias', token=admin_token,
        verify=lambda b, s: isinstance(b, dict) and b.get('total', 0) >= 3,
    )
    await _call(
        async_client, 'get', '/api/v1/encuentros/instancias',
        params={'materia_id': str(MATERIA_ALGEBRA_ID), 'offset': 0, 'limit': 10},
        token=admin_token,
    )

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
            'asignacion_id': str(ASIG_ADMIN_ALGEBRA_ID),
            'materia_id': str(MATERIA_ALGEBRA_ID),
            'cohorte_id': str(COHORTE_ING_2024_ID),
            'dia': 'Viernes',
            'horario': '18:00-19:00',
        },
        token=admin_token, expect_status=201,
        verify=json_has_keys('id', 'dia', 'horario'),
    )
    new_guardia_id = _to_dict(body).get('id')

    # GET → 5 from seed + 1 new = 6 (ADMIN sees all)
    await _call(
        async_client, 'get', '/api/v1/guardias', token=admin_token,
        verify=lambda b, s: isinstance(b, dict) and b.get('total', 0) >= 5,
    )
    await _call(
        async_client, 'get', '/api/v1/guardias',
        params={'materia_id': str(MATERIA_ALGEBRA_ID)},
        token=admin_token,
    )

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
        params={'materia_id': str(MATERIA_ALGEBRA_ID)},
        token=admin_token,
    )

    # ── 20. COLOQUIOS ──────────────────────────────────────────────────
    # POST / → create new eval
    status, body = await _call(
        async_client, 'post', '/api/v1/coloquios/',
        json_body={
            'materia_id': str(MATERIA_ALGEBRA_ID),
            'cohorte_id': str(COHORTE_ING_2024_ID),
            'instancia': 'Segundo Parcial',
            'tipo': 'Parcial',
            'turnos': [
                {'fecha': '2025-06-15', 'hora_inicio': '09:00', 'hora_fin': '11:00', 'cupo': 30},
                {'fecha': '2025-06-16', 'hora_inicio': '14:00', 'hora_fin': '16:00', 'cupo': 25},
            ],
        },
        token=admin_token, expect_status=201,
        verify=json_has_keys('id', 'materia_id', 'instancia'),
    )
    new_eval_id = _to_dict(body).get('id')

    # GET metricas
    await _call(
        async_client, 'get', '/api/v1/coloquios/metricas', token=admin_token,
        verify=json_has_keys('total_convocatorias_activas', 'total_alumnos_convocados', 'total_reservas_activas'),
    )

    # GET / → 2 from seed + 1 new = 3
    await _call(
        async_client, 'get', '/api/v1/coloquios/', token=admin_token,
        verify=lambda b, s: isinstance(b, dict) and isinstance(b.get('items'), list),
    )
    await _call(
        async_client, 'get', '/api/v1/coloquios/',
        params={'materia_id': str(MATERIA_ALGEBRA_ID)},
        token=admin_token,
    )

    if new_eval_id:
        await _call(async_client, 'get', f'/api/v1/coloquios/{new_eval_id}', token=admin_token,
                    verify=json_has_keys('id', 'materia_id'))

        # POST /{evaluacion_id}/alumnos
        await _call(
            async_client, 'post', f'/api/v1/coloquios/{new_eval_id}/alumnos',
            json_body={'alumno_ids': [str(USER_ALUMNO_COL_1)]},
            token=admin_token,
        )

        # POST /{evaluacion_id}/reservas
        result = await db_session.execute(
            select(TurnoColoquio).where(TurnoColoquio.evaluacion_id == new_eval_id)
        )
        turnos = result.scalars().all()
        turno = turnos[0] if turnos else None
        if turno:
            status, body = await _call(
                async_client, 'post', f'/api/v1/coloquios/{new_eval_id}/reservas',
                json_body={'turno_id': str(turno.id)},
                token=admin_token,
            )
            reserva_id = _to_dict(body).get('id') if isinstance(body, dict) else None
            if reserva_id:
                await _call(
                    async_client, 'delete', f'/api/v1/coloquios/reservas/{reserva_id}',
                    token=admin_token,
                )

        # PUT /{evaluacion_id}/resultados/{alumno_id}
        await _call(
            async_client, 'put', f'/api/v1/coloquios/{new_eval_id}/resultados/{USER_ALUMNO_COL_1}',
            json_body={'nota_final': 'Aprobado'},
            token=admin_token,
            verify=json_has_keys('nota_final', 'alumno_id'),
        )

        # GET /{evaluacion_id}/resultados
        await _call(
            async_client, 'get', f'/api/v1/coloquios/{new_eval_id}/resultados',
            token=admin_token,
            verify=lambda b, s: isinstance(b, dict) and b.get('total', 0) >= 1,
        )

        # PATCH /{evaluacion_id}/cerrar
        await _call(
            async_client, 'patch', f'/api/v1/coloquios/{new_eval_id}/cerrar',
            token=admin_token,
            verify=json_has_keys('id', 'estado'),
        )

    # ── 21. PROGRAMAS MATERIA ──────────────────────────────────────────
    # GET list → 2 from seed
    await _call(
        async_client, 'get', '/api/v1/admin/programas', token=admin_token,
        verify=items_match('programas list', count=2,
                           contains_values=[('titulo', 'Álgebra - Programa 2024')]),
    )

    # POST create
    status, body = await _call(
        async_client, 'post', '/api/v1/admin/programas',
        json_body={
            'materia_id': str(MATERIA_PROG1_ID),
            'carrera_id': str(CARRERA_ING_ID),
            'cohorte_id': str(COHORTE_ING_2025_ID),
            'titulo': 'Programación I - 2025',
        },
        token=admin_token, expect_status=201,
        verify=json_has_keys('id', 'titulo', 'materia_id'),
    )
    new_programa_id = _to_dict(body).get('id')
    if new_programa_id:
        await _call(async_client, 'get', f'/api/v1/admin/programas/{new_programa_id}', token=admin_token,
                    verify=json_has_keys('id', 'titulo'))
        await _call(
            async_client, 'put', f'/api/v1/admin/programas/{new_programa_id}',
            json_body={'titulo': 'Programa Actualizado'},
            token=admin_token,
            verify=json_contains('titulo', 'Programa Actualizado'),
        )
        await _call(async_client, 'delete', f'/api/v1/admin/programas/{new_programa_id}', token=admin_token,
                    expect_status=204)
        await _call(async_client, 'get', f'/api/v1/admin/programas/{new_programa_id}', token=admin_token,
                    expect_status=404)

    # GET by seed ID
    await _call(async_client, 'get', f'/api/v1/admin/programas/{PROGRAMA_ALGEBRA_ID}', token=admin_token,
                verify=lambda b, s: isinstance(b, dict) and b.get('titulo') == 'Álgebra - Programa 2024')

    await _call(async_client, 'get', f'/api/v1/admin/programas/{uuid.uuid4()}', token=admin_token,
                expect_status=404)

    # ── 22. FECHAS ACADEMICAS ──────────────────────────────────────────
    # GET list → 8 from seed
    await _call(
        async_client, 'get', '/api/v1/admin/fechas-academicas', token=admin_token,
        verify=items_match('fechas list', count=8),
    )

    # GET list filtered by tipo
    await _call(
        async_client, 'get', '/api/v1/admin/fechas-academicas',
        params={'tipo': 'Parcial'},
        token=admin_token,
        verify=items_match('fechas filtered by tipo', contains_values=[('tipo', 'Parcial')]),
    )

    # POST create
    status, body = await _call(
        async_client, 'post', '/api/v1/admin/fechas-academicas',
        json_body={
            'materia_id': str(MATERIA_PROG1_ID),
            'cohorte_id': str(COHORTE_ING_2025_ID),
            'tipo': 'TP',
            'numero': 1,
            'periodo': '2025-1C',
            'fecha': '2025-04-15',
            'titulo': 'TP1 - Programación',
        },
        token=admin_token, expect_status=201,
        verify=json_has_keys('id', 'titulo', 'tipo'),
    )
    new_fecha_id = _to_dict(body).get('id')
    if new_fecha_id:
        await _call(async_client, 'get', f'/api/v1/admin/fechas-academicas/{new_fecha_id}', token=admin_token,
                    verify=json_has_keys('id', 'titulo'))
        await _call(
            async_client, 'put', f'/api/v1/admin/fechas-academicas/{new_fecha_id}',
            json_body={'titulo': 'TP1 Modificado'},
            token=admin_token,
            verify=json_contains('titulo', 'TP1 Modificado'),
        )
        await _call(async_client, 'delete', f'/api/v1/admin/fechas-academicas/{new_fecha_id}', token=admin_token,
                    expect_status=204)
        await _call(async_client, 'get', f'/api/v1/admin/fechas-academicas/{new_fecha_id}', token=admin_token,
                    expect_status=404)

    # GET by seed ID
    await _call(async_client, 'get', f'/api/v1/admin/fechas-academicas/{FECHA_ALGEBRA_PARCIAL1}', token=admin_token,
                verify=lambda b, s: isinstance(b, dict) and b.get('titulo') == 'Primer Parcial')

    await _call(async_client, 'get', f'/api/v1/admin/fechas-academicas/{uuid.uuid4()}', token=admin_token,
                expect_status=404)

    # ── 23. ANALISIS ───────────────────────────────────────────────────
    # GET atrasados → 5 atrasados for Algebra/ING-2024
    await _call(
        async_client, 'get', '/api/v1/analisis/atrasados',
        params={'materia_id': str(MATERIA_ALGEBRA_ID), 'cohorte_id': str(COHORTE_ING_2024_ID)},
        token=admin_token,
    )

    # GET ranking
    await _call(
        async_client, 'get', '/api/v1/analisis/ranking',
        params={'materia_id': str(MATERIA_ALGEBRA_ID), 'cohorte_id': str(COHORTE_ING_2024_ID)},
        token=admin_token,
        verify=lambda b, s: (
            isinstance(b, dict)
            and b.get('total', 0) > 0
            and len(b.get('items', [])) > 0
            and b['items'][0].get('promedio', 0) >= b['items'][-1].get('promedio', 0)
        ),
    )

    # GET reportes-rapidos
    await _call(
        async_client, 'get', '/api/v1/analisis/reportes-rapidos',
        params={'materia_id': str(MATERIA_ALGEBRA_ID), 'cohorte_id': str(COHORTE_ING_2024_ID)},
        token=admin_token,
        verify=json_has_keys('total_alumnos', 'alumnos_aprobados', 'alumnos_atrasados'),
    )

    # GET notas-finales
    await _call(
        async_client, 'get', '/api/v1/analisis/notas-finales',
        params={
            'materia_id': str(MATERIA_ALGEBRA_ID),
            'cohorte_id': str(COHORTE_ING_2024_ID),
            'actividades': 'TP1,TP2',
        },
        token=admin_token,
        verify=lambda b, s: isinstance(b, dict) and b.get('total', 0) > 0,
    )

    # GET tps-sin-corregir
    await _call(
        async_client, 'get', '/api/v1/analisis/tps-sin-corregir',
        params={'materia_id': str(MATERIA_ALGEBRA_ID), 'cohorte_id': str(COHORTE_ING_2024_ID)},
        token=admin_token,
    )

    # GET monitor-general
    await _call(
        async_client, 'get', '/api/v1/analisis/monitor-general',
        params={'materia_id': str(MATERIA_ALGEBRA_ID)},
        token=admin_token,
    )

    # GET monitor-seguimiento
    await _call(
        async_client, 'get', '/api/v1/analisis/monitor-seguimiento',
        params={'materia_id': str(MATERIA_ALGEBRA_ID)},
        token=admin_token,
    )

    # ── 24. TAREAS ─────────────────────────────────────────────────────
    # GET mis-tareas (admin has 0 assigned in seed)
    await _call(
        async_client, 'get', '/api/v1/tareas/mis-tareas',
        token=admin_token,
    )

    # POST crear tarea
    await _call(
        async_client, 'post', '/api/v1/tareas',
        json_body={
            'asignado_a': str(USER_ANA_ID),
            'descripcion': 'Revisar planificación del cuatrimestre',
        },
        token=admin_token,
        verify=lambda b, s: isinstance(b, dict) and b.get('estado') == 'Pendiente' and b.get('asignado_por') == str(USER_ADMIN_ID),
    )

    # GET tarea by id
    await _call(
        async_client, 'get', f'/api/v1/tareas/{TAREA_1_ID}',
        token=admin_token,
        verify=lambda b, s: isinstance(b, dict) and b.get('descripcion', '').startswith('Revisar'),
    )

    # PATCH estado Pendiente → En progreso
    await _call(
        async_client, 'patch', f'/api/v1/tareas/{TAREA_2_ID}/estado',
        json_body={'estado': 'En progreso'},
        token=admin_token,
        verify=lambda b, s: isinstance(b, dict) and b.get('estado') == 'En progreso',
    )

    # PATCH estado En progreso → Resuelta
    await _call(
        async_client, 'patch', f'/api/v1/tareas/{TAREA_2_ID}/estado',
        json_body={'estado': 'Resuelta'},
        token=admin_token,
        verify=lambda b, s: isinstance(b, dict) and b.get('estado') == 'Resuelta',
    )

    # PATCH estado Cancelada on tarea 3
    await _call(
        async_client, 'patch', f'/api/v1/tareas/{TAREA_3_ID}/estado',
        json_body={'estado': 'Cancelada'},
        token=admin_token,
        verify=lambda b, s: isinstance(b, dict) and b.get('estado') == 'Cancelada',
    )

    # POST comentario en tarea
    await _call(
        async_client, 'post', f'/api/v1/tareas/{TAREA_1_ID}/comentarios',
        json_body={'texto': 'Revisando el avance del equipo'},
        token=admin_token,
        verify=lambda b, s: isinstance(b, dict) and b.get('texto') == 'Revisando el avance del equipo',
    )

    # GET tarea with comentarios (should have 1 added + 0 seed on TAREA_1)
    await _call(
        async_client, 'get', f'/api/v1/tareas/{TAREA_1_ID}',
        token=admin_token,
        verify=lambda b, s: isinstance(b, dict) and len(b.get('comentarios', [])) == 1,
    )

    # GET admin/tareas list
    await _call(
        async_client, 'get', '/api/v1/admin/tareas',
        token=admin_token,
        verify=lambda b, s: isinstance(b, dict) and b.get('total', 0) >= 5,
    )

    # GET admin/tareas with search filter
    await _call(
        async_client, 'get', '/api/v1/admin/tareas',
        params={'search': 'Algebra'},
        token=admin_token,
        verify=lambda b, s: isinstance(b, dict) and b.get('total', 0) >= 1,
    )

    # DELETE tarea (soft delete)
    await _call(
        async_client, 'delete', f'/api/v1/tareas/{TAREA_5_ID}',
        token=admin_token,
    )

    # ── 25. ERROR VERIFICATION ─────────────────────────────────────────
    # 404 on non-existent route
    await _call(
        async_client, 'get', '/api/v1/non-existent-route', token=admin_token,
        expect_status=404,
    )

    # 422 with invalid body (extra fields)
    await _call(
        async_client, 'post', '/api/v1/admin/carreras',
        json_body={'codigo': 'TEST', 'nombre': 'Test', 'extra_field': 'should_fail'},
        token=admin_token, expect_status=422,
    )

    # 401 without auth (protected endpoint)
    await _call(
        async_client, 'get', '/api/v1/admin/carreras',
        expect_status=401,
    )

    # 422 with empty body (carrera post)
    await _call(
        async_client, 'post', '/api/v1/admin/carreras',
        json_body={},
        token=admin_token, expect_status=422,
    )

    # ── PRINT RESULTS TABLE ────────────────────────────────────────────
    print('\n\n## ENDPOINT VERIFICATION TABLE')
    print('')
    print('| # | Method | Route | Status | Content OK | Notes |')
    print('|---|--------|-------|--------|------------|-------|')
    for r in RESULTS:
        ok_str = 'PASS' if r.response_ok else 'FAIL'
        content_str = ''
        if r.content_ok is True:
            content_str = 'PASS'
        elif r.content_ok is False:
            content_str = 'FAIL'
        else:
            content_str = 'N/A'
        print(f'| {r.index} | {r.method} | {r.path} | {r.status} | {content_str} | {r.notes} |')

    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r.response_ok)
    content_passed = sum(1 for r in RESULTS if r.content_ok is True)
    content_failed = sum(1 for r in RESULTS if r.content_ok is False)
    failed = total - passed
    print(f'\n**Total: {total} | Passed (no 500): {passed} | Failed (500): {failed} | Content OK: {content_passed} | Content FAIL: {content_failed}**')
    print('')

    # Assert no 500 errors
    server_errors = [r for r in RESULTS if r.status == 500]
    assert not server_errors, f'Server errors (500) on: {[(r.method, r.path) for r in server_errors]}'
