"""Integration tests for liquidaciones endpoints using run_seed()."""

from datetime import date

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.services.grilla_salarial_service import GrillaSalarialService
from seed import (
    run_seed,
    TENANT_ID,
    USER_ADMIN_ID,
    COHORTE_ING_2024_ID,
)


@pytest.mark.asyncio
async def test_liquidaciones_list_empty(db_session: AsyncSession, async_client: AsyncClient):
    await run_seed(db_session)
    token = create_access_token(str(USER_ADMIN_ID), str(TENANT_ID), ['ADMIN'])
    response = await async_client.get(
        '/api/v1/liquidaciones',
        params={'cohorte_id': str(COHORTE_ING_2024_ID), 'periodo': '2026-04'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_calcular_liquidacion(db_session: AsyncSession, async_client: AsyncClient):
    await run_seed(db_session)
    token = create_access_token(str(USER_ADMIN_ID), str(TENANT_ID), ['ADMIN'])

    # Set up base salary first
    grilla = GrillaSalarialService(db_session, TENANT_ID)
    await grilla.crear_base(rol='PROFESOR', monto=500000, desde=date(2026, 1, 1))
    await grilla.crear_base(rol='TUTOR', monto=300000, desde=date(2026, 1, 1))
    await db_session.flush()

    response = await async_client.post(
        '/api/v1/liquidaciones/calcular',
        json={'cohorte_id': str(COHORTE_ING_2024_ID), 'periodo': '2026-04'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert 'total' in data[0]
        assert 'monto_base' in data[0]


@pytest.mark.asyncio
async def test_cerrar_liquidacion(db_session: AsyncSession, async_client: AsyncClient):
    await run_seed(db_session)
    token = create_access_token(str(USER_ADMIN_ID), str(TENANT_ID), ['ADMIN'])

    # Set up base salary and calculate first
    grilla = GrillaSalarialService(db_session, TENANT_ID)
    await grilla.crear_base(rol='PROFESOR', monto=500000, desde=date(2026, 1, 1))
    await grilla.crear_base(rol='TUTOR', monto=300000, desde=date(2026, 1, 1))
    await db_session.flush()

    calc_resp = await async_client.post(
        '/api/v1/liquidaciones/calcular',
        json={'cohorte_id': str(COHORTE_ING_2024_ID), 'periodo': '2026-04'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert calc_resp.status_code == 200

    response = await async_client.post(
        f'/api/v1/liquidaciones/cerrar/{COHORTE_ING_2024_ID}/2026-04',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == 200
    data = response.json()
    assert 'cerradas' in data
    assert data['cerradas'] > 0


@pytest.mark.asyncio
async def test_exportar_csv(db_session: AsyncSession, async_client: AsyncClient):
    await run_seed(db_session)
    token = create_access_token(str(USER_ADMIN_ID), str(TENANT_ID), ['ADMIN'])

    grilla = GrillaSalarialService(db_session, TENANT_ID)
    await grilla.crear_base(rol='PROFESOR', monto=500000, desde=date(2026, 1, 1))
    await grilla.crear_base(rol='TUTOR', monto=300000, desde=date(2026, 1, 1))
    await db_session.flush()

    await async_client.post(
        '/api/v1/liquidaciones/calcular',
        json={'cohorte_id': str(COHORTE_ING_2024_ID), 'periodo': '2026-04'},
        headers={'Authorization': f'Bearer {token}'},
    )

    response = await async_client.get(
        '/api/v1/liquidaciones/exportar',
        params={'cohorte_id': str(COHORTE_ING_2024_ID), 'periodo': '2026-04'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == 200
    assert 'text/csv' in response.headers.get('content-type', '')


@pytest.mark.asyncio
async def test_facturas_list(db_session: AsyncSession, async_client: AsyncClient):
    await run_seed(db_session)
    token = create_access_token(str(USER_ADMIN_ID), str(TENANT_ID), ['ADMIN'])
    response = await async_client.get(
        '/api/v1/facturas',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
