"""Integration tests that use seed.run_seed() to populate a known DB state."""

from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from seed import (
    run_seed,
    COHORTE_ING_2024_ID,
    MATERIA_ALGEBRA_ID,
    MATERIA_CONTABILIDAD_ID,
    TENANT_ID,
    USER_ADMIN_ID,
    LOTE_COM_ID,
)


@pytest.mark.asyncio
async def test_atrasados_detectados(db_session: AsyncSession, async_client: AsyncClient) -> None:
    await run_seed(db_session)
    token = create_access_token(str(USER_ADMIN_ID), str(TENANT_ID), ['ADMIN'])
    response = await async_client.get(
        '/api/v1/analisis/atrasados',
        params={'materia_id': str(MATERIA_ALGEBRA_ID), 'cohorte_id': str(COHORTE_ING_2024_ID)},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['total'] == 5
    assert len(data['items']) == 5


@pytest.mark.asyncio
async def test_ranking_ordenado(db_session: AsyncSession, async_client: AsyncClient) -> None:
    await run_seed(db_session)
    token = create_access_token(str(USER_ADMIN_ID), str(TENANT_ID), ['ADMIN'])
    response = await async_client.get(
        '/api/v1/analisis/ranking',
        params={'materia_id': str(MATERIA_CONTABILIDAD_ID), 'cohorte_id': str(COHORTE_ING_2024_ID)},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == 200
    data = response.json()
    items = data['items']
    for i in range(len(items) - 1):
        assert items[i]['actividades_aprobadas'] >= items[i + 1]['actividades_aprobadas']


@pytest.mark.asyncio
async def test_comunicaciones_por_estado(db_session: AsyncSession, async_client: AsyncClient) -> None:
    await run_seed(db_session)
    token = create_access_token(str(USER_ADMIN_ID), str(TENANT_ID), ['ADMIN'])
    response = await async_client.get(
        '/api/v1/comunicaciones',
        params={'lote_id': str(LOTE_COM_ID)},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['total'] >= 5
    estados = {item['estado'] for item in data['items']}
    assert 'Pendiente' in estados
    assert 'Enviado' in estados


@pytest.mark.asyncio
async def test_avisos_vigentes(db_session: AsyncSession, async_client: AsyncClient) -> None:
    await run_seed(db_session)
    token = create_access_token(str(USER_ADMIN_ID), str(TENANT_ID), ['ADMIN'])
    response = await async_client.get(
        '/api/v1/avisos',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == 200
    data = response.json()
    items = data.get('items', data)
    assert len(items) >= 1
    now = datetime.now(timezone.utc)
    for item in items:
        fin = datetime.fromisoformat(item['fin_vigencia'])
        assert fin > now, f'Aviso {item["titulo"]} has fin_vigencia in the past'


@pytest.mark.asyncio
async def test_encuentros_exist(db_session: AsyncSession, async_client: AsyncClient) -> None:
    await run_seed(db_session)
    token = create_access_token(str(USER_ADMIN_ID), str(TENANT_ID), ['ADMIN'])
    response = await async_client.get(
        '/api/v1/encuentros/slots',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == 200
    data = response.json()
    items = data.get('items', data)
    assert len(items) >= 3


@pytest.mark.asyncio
async def test_guardias_exist(db_session: AsyncSession, async_client: AsyncClient) -> None:
    await run_seed(db_session)
    token = create_access_token(str(USER_ADMIN_ID), str(TENANT_ID), ['ADMIN'])
    response = await async_client.get(
        '/api/v1/guardias',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['total'] >= 5


@pytest.mark.asyncio
async def test_coloquios_exist(db_session: AsyncSession, async_client: AsyncClient) -> None:
    await run_seed(db_session)
    token = create_access_token(str(USER_ADMIN_ID), str(TENANT_ID), ['ADMIN'])
    response = await async_client.get(
        '/api/v1/coloquios/',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['total'] >= 2


@pytest.mark.asyncio
async def test_umbral_update(db_session: AsyncSession, async_client: AsyncClient) -> None:
    await run_seed(db_session)
    token = create_access_token(str(USER_ADMIN_ID), str(TENANT_ID), ['ADMIN'])
    response = await async_client.put(
        f'/api/v1/umbrales/{MATERIA_ALGEBRA_ID}/{COHORTE_ING_2024_ID}',
        json={'umbral_pct': 70, 'valores_aprobatorios': ['Aprobado', 'Satisfactorio']},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['umbral_pct'] == 70
    assert data['valores_aprobatorios'] == ['Aprobado', 'Satisfactorio']
