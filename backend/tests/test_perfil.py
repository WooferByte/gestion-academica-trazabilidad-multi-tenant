import uuid

import pytest
import pytest_asyncio

from app.core.security import create_access_token, encrypt, hash_password
from app.models.tenant import Tenant
from app.models.user import User
from tests.helpers import _create_tenant, _create_user


@pytest_asyncio.fixture
async def tenant(db_session):
    return await _create_tenant(db_session)


@pytest_asyncio.fixture
async def user(db_session, tenant):
    u = User(
        tenant_id=tenant.id,
        email='user@test.com',
        password_hash=hash_password('pass123'),
        nombre_cifrado=encrypt('Juan'),
        apellido_cifrado=encrypt('Pérez'),
        dni_cifrado=encrypt('12345678'),
        cuil_cifrado=encrypt('20-12345678-9'),
        cbu_cifrado=encrypt('0000003100012345678901'),
        alias_cbu_cifrado=encrypt('juan.perez'),
        banco='Banco Test',
        regional='Cuyo',
        facturador=True,
        estado='Activo',
        roles=['docente'],
    )
    db_session.add(u)
    await db_session.flush()
    return u


@pytest_asyncio.fixture
async def user_token(db_session, user):
    return create_access_token(str(user.id), str(user.tenant_id), user.roles)


class TestGetPerfil:
    @pytest.mark.asyncio
    async def test_get_perfil_returns_decrypted_data(self, async_client, user, user_token):
        response = await async_client.get(
            '/api/v1/perfil',
            headers={'Authorization': f'Bearer {user_token}'},
        )
        assert response.status_code == 200
        data = response.json()
        assert data['nombre'] == 'Juan'
        assert data['apellido'] == 'Pérez'
        assert data['dni'] == '12345678'
        assert data['cuil'] == '20-12345678-9'
        assert data['cbu'] == '0000003100012345678901'
        assert data['alias_cbu'] == 'juan.perez'
        assert data['banco'] == 'Banco Test'
        assert data['regional'] == 'Cuyo'
        assert data['facturador'] is True
        assert data['email'] == 'user@test.com'

    @pytest.mark.asyncio
    async def test_get_perfil_returns_401_without_auth(self, async_client):
        response = await async_client.get('/api/v1/perfil')
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_perfil_isolation(self, db_session, async_client, tenant):
        user_a = User(
            tenant_id=tenant.id,
            email='a@test.com',
            password_hash=hash_password('pass'),
            nombre_cifrado=encrypt('Alice'),
            roles=['docente'],
        )
        db_session.add(user_a)
        await db_session.flush()
        token_a = create_access_token(str(user_a.id), str(tenant.id), user_a.roles)

        tenant_b = Tenant(nombre='Other', codigo='OTH')
        db_session.add(tenant_b)
        await db_session.flush()
        user_b = User(
            tenant_id=tenant_b.id,
            email='b@test.com',
            password_hash=hash_password('pass'),
            nombre_cifrado=encrypt('Bob'),
            roles=['docente'],
        )
        db_session.add(user_b)
        await db_session.flush()

        response = await async_client.get(
            '/api/v1/perfil',
            headers={'Authorization': f'Bearer {token_a}'},
        )
        assert response.status_code == 200
        data = response.json()
        assert data['nombre'] == 'Alice'
        assert data['tenant_id'] == str(tenant.id)


class TestPutPerfil:
    @pytest.mark.asyncio
    async def test_update_editable_fields(self, async_client, user, user_token):
        response = await async_client.put(
            '/api/v1/perfil',
            json={
                'nombre': 'Carlos',
                'banco': 'Banco Nuevo',
                'regional': 'Patagonia',
                'facturador': False,
            },
            headers={'Authorization': f'Bearer {user_token}'},
        )
        assert response.status_code == 200
        data = response.json()
        assert data['nombre'] == 'Carlos'
        assert data['banco'] == 'Banco Nuevo'
        assert data['regional'] == 'Patagonia'
        assert data['facturador'] is False

    @pytest.mark.asyncio
    async def test_cuil_rejected_by_schema(self, async_client, user, user_token):
        response = await async_client.put(
            '/api/v1/perfil',
            json={'cuil': '20-99999999-9'},
            headers={'Authorization': f'Bearer {user_token}'},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_extra_fields_rejected(self, async_client, user, user_token):
        response = await async_client.put(
            '/api/v1/perfil',
            json={'nombre': 'Test', 'campo_inventado': 'value'},
            headers={'Authorization': f'Bearer {user_token}'},
        )
        assert response.status_code == 422
