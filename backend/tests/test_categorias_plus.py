import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core.dependencies import get_db
from app.core.security import create_access_token
from app.main import create_app
from app.models.categoria_plus import CategoriaPlus
from app.models.materia import Materia
from app.models.tenant import Tenant
from app.models.user import User
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user_role import UserRole


def _make_cat_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest_asyncio.fixture
async def setup_data(db_session):
    tid = uuid.uuid4()
    tenant = Tenant(id=tid, nombre='Test', codigo='TST-CP', estado='Activo')
    db_session.add(tenant)

    admin_user = User(tenant_id=tid, email='admin@cp.com', password_hash='x', roles=['ADMIN'])
    db_session.add(admin_user)
    await db_session.flush()

    role = Role(tenant_id=tid, name='ADMIN', codigo='ADMIN')
    db_session.add(role)
    await db_session.flush()

    perm = Permission(tenant_id=tid, codigo='estructura:gestionar', modulo='estructura', accion='gestionar')
    db_session.add(perm)
    await db_session.flush()

    db_session.add(RolePermission(tenant_id=tid, role_id=role.id, permiso_id=perm.id))
    db_session.add(UserRole(tenant_id=tid, user_id=admin_user.id, role_id=role.id))
    await db_session.flush()

    token = create_access_token(str(admin_user.id), str(tid), ['ADMIN'])

    return {
        'tid': tid,
        'admin_user': admin_user,
        'token': token,
    }


class TestCRUD:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        c = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        c.headers['Authorization'] = f'Bearer {token}'
        return c

    @pytest.mark.asyncio
    async def test_create_categoria_201(self, app, db_session, setup_data):
        async with await self._client(app, db_session, setup_data['token']) as c:
            resp = await c.post('/api/v1/admin/categorias-plus', json={
                'codigo': 'PLUS-01',
                'nombre': 'Categoría Premium',
                'activo': True,
            })
        assert resp.status_code == 201
        data = resp.json()
        assert data['codigo'] == 'PLUS-01'
        assert data['nombre'] == 'Categoría Premium'
        assert data['activo'] is True
        assert data['tenant_id'] == str(setup_data['tid'])

    @pytest.mark.asyncio
    async def test_create_categoria_duplicate_codigo_case_insensitive_409(self, app, db_session, setup_data):
        async with await self._client(app, db_session, setup_data['token']) as c:
            await c.post('/api/v1/admin/categorias-plus', json={
                'codigo': 'PLUS-01',
                'nombre': 'Original',
            })
            resp = await c.post('/api/v1/admin/categorias-plus', json={
                'codigo': 'plus-01',
                'nombre': 'Duplicado',
            })
        assert resp.status_code == 409
        assert 'código' in resp.json()['detail'].lower()

    @pytest.mark.asyncio
    async def test_create_categoria_default_activo(self, app, db_session, setup_data):
        async with await self._client(app, db_session, setup_data['token']) as c:
            resp = await c.post('/api/v1/admin/categorias-plus', json={
                'codigo': 'PLUS-02',
                'nombre': 'Sin activo explícito',
            })
        assert resp.status_code == 201
        assert resp.json()['activo'] is True

    @pytest.mark.asyncio
    async def test_list_categorias(self, app, db_session, setup_data):
        cat_a = CategoriaPlus(tenant_id=setup_data['tid'], codigo='A', nombre='Cat A', activo=True)
        cat_b = CategoriaPlus(tenant_id=setup_data['tid'], codigo='B', nombre='Cat B', activo=True)
        db_session.add_all([cat_a, cat_b])
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['token']) as c:
            resp = await c.get('/api/v1/admin/categorias-plus')
        assert resp.status_code == 200
        data = resp.json()
        assert data['total'] == 2
        codigos = {i['codigo'] for i in data['items']}
        assert codigos == {'A', 'B'}

    @pytest.mark.asyncio
    async def test_get_categoria_by_id(self, app, db_session, setup_data):
        cat = CategoriaPlus(tenant_id=setup_data['tid'], codigo='GET', nombre='Get me', activo=True)
        db_session.add(cat)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['token']) as c:
            resp = await c.get(f'/api/v1/admin/categorias-plus/{cat.id}')
        assert resp.status_code == 200
        assert resp.json()['codigo'] == 'GET'

    @pytest.mark.asyncio
    async def test_get_categoria_not_found_404(self, app, db_session, setup_data):
        async with await self._client(app, db_session, setup_data['token']) as c:
            resp = await c.get(f'/api/v1/admin/categorias-plus/{uuid.uuid4()}')
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_update_categoria(self, app, db_session, setup_data):
        cat = CategoriaPlus(tenant_id=setup_data['tid'], codigo='OLD', nombre='Old name', activo=True)
        db_session.add(cat)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['token']) as c:
            resp = await c.put(f'/api/v1/admin/categorias-plus/{cat.id}', json={
                'nombre': 'New name',
                'codigo': 'NEW',
            })
        assert resp.status_code == 200
        assert resp.json()['nombre'] == 'New name'
        assert resp.json()['codigo'] == 'NEW'

    @pytest.mark.asyncio
    async def test_update_categoria_codigo_duplicate_409(self, app, db_session, setup_data):
        cat_a = CategoriaPlus(tenant_id=setup_data['tid'], codigo='A', nombre='Cat A', activo=True)
        cat_b = CategoriaPlus(tenant_id=setup_data['tid'], codigo='B', nombre='Cat B', activo=True)
        db_session.add_all([cat_a, cat_b])
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['token']) as c:
            resp = await c.put(f'/api/v1/admin/categorias-plus/{cat_b.id}', json={'codigo': 'A'})
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_soft_delete_categoria(self, app, db_session, setup_data):
        cat = CategoriaPlus(tenant_id=setup_data['tid'], codigo='DEL', nombre='Delete me', activo=True)
        db_session.add(cat)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['token']) as c:
            resp = await c.delete(f'/api/v1/admin/categorias-plus/{cat.id}')
        assert resp.status_code == 204

        result = await db_session.execute(
            select(CategoriaPlus).where(CategoriaPlus.id == cat.id)
        )
        deleted = result.scalar_one()
        assert deleted.deleted_at is not None

    @pytest.mark.asyncio
    async def test_delete_categoria_con_materias_protegido_409(self, app, db_session, setup_data):
        cat = CategoriaPlus(tenant_id=setup_data['tid'], codigo='PROT', nombre='Protegida', activo=True)
        db_session.add(cat)
        await db_session.flush()

        materia = Materia(
            tenant_id=setup_data['tid'], codigo='MAT-PROT', nombre='Materia protegida',
            categoria_plus_id=cat.id,
        )
        db_session.add(materia)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['token']) as c:
            resp = await c.delete(f'/api/v1/admin/categorias-plus/{cat.id}')
        assert resp.status_code == 409
        assert 'materias' in resp.json()['detail'].lower()

    @pytest.mark.asyncio
    async def test_403_sin_permiso(self, app, db_session, setup_data):
        tid = setup_data['tid']
        other_user = User(tenant_id=tid, email='noperm@cp.com', password_hash='x', roles=['ALUMNO'])
        db_session.add(other_user)
        await db_session.flush()
        no_perm_token = create_access_token(str(other_user.id), str(tid), ['ALUMNO'])

        async with await self._client(app, db_session, no_perm_token) as c:
            resp = await c.post('/api/v1/admin/categorias-plus', json={
                'codigo': 'NO-PERM', 'nombre': 'Sin permiso',
            })
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_422_campo_extra(self, app, db_session, setup_data):
        async with await self._client(app, db_session, setup_data['token']) as c:
            resp = await c.post('/api/v1/admin/categorias-plus', json={
                'codigo': 'EXTRA', 'nombre': 'Extra field', 'extra': 'no_permitido',
            })
        assert resp.status_code == 422


class TestToggle:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        c = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        c.headers['Authorization'] = f'Bearer {token}'
        return c

    @pytest.mark.asyncio
    async def test_toggle_desactivar(self, app, db_session, setup_data):
        cat = CategoriaPlus(tenant_id=setup_data['tid'], codigo='TOGGLE', nombre='Toggle me', activo=True)
        db_session.add(cat)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['token']) as c:
            resp = await c.patch(f'/api/v1/admin/categorias-plus/{cat.id}/toggle')
        assert resp.status_code == 200
        assert resp.json()['activo'] is False

    @pytest.mark.asyncio
    async def test_toggle_desactivar_nullifica_materias(self, app, db_session, setup_data):
        cat = CategoriaPlus(tenant_id=setup_data['tid'], codigo='NULL-CAT', nombre='Nullify test', activo=True)
        db_session.add(cat)
        await db_session.flush()

        materia = Materia(
            tenant_id=setup_data['tid'], codigo='MAT-NULL', nombre='Materia a nullificar',
            categoria_plus_id=cat.id,
        )
        db_session.add(materia)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['token']) as c:
            resp = await c.patch(f'/api/v1/admin/categorias-plus/{cat.id}/toggle')
        assert resp.status_code == 200
        assert resp.json()['activo'] is False

        result = await db_session.execute(
            select(Materia).where(Materia.id == materia.id)
        )
        materia_refreshed = result.scalar_one()
        assert materia_refreshed.categoria_plus_id is None

    @pytest.mark.asyncio
    async def test_toggle_reactivar(self, app, db_session, setup_data):
        cat = CategoriaPlus(tenant_id=setup_data['tid'], codigo='REACT', nombre='Reactivate', activo=False)
        db_session.add(cat)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['token']) as c:
            resp = await c.patch(f'/api/v1/admin/categorias-plus/{cat.id}/toggle')
        assert resp.status_code == 200
        assert resp.json()['activo'] is True

    @pytest.mark.asyncio
    async def test_toggle_404_inexistente(self, app, db_session, setup_data):
        async with await self._client(app, db_session, setup_data['token']) as c:
            resp = await c.patch(f'/api/v1/admin/categorias-plus/{uuid.uuid4()}/toggle')
        assert resp.status_code == 404


class TestAsignacion:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        c = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        c.headers['Authorization'] = f'Bearer {token}'
        return c

    @pytest.mark.asyncio
    async def test_asignar_categoria_a_materia(self, app, db_session, setup_data):
        cat = CategoriaPlus(tenant_id=setup_data['tid'], codigo='ASIG-CAT', nombre='Categoria asignable', activo=True)
        db_session.add(cat)
        await db_session.flush()

        materia = Materia(tenant_id=setup_data['tid'], codigo='ASIG-MAT', nombre='Materia a asignar')
        db_session.add(materia)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['token']) as c:
            resp = await c.put(
                f'/api/v1/admin/materias/{materia.id}/categoria',
                json={'categoria_plus_id': str(cat.id)},
            )
        assert resp.status_code == 200
        assert resp.json()['categoria_plus_id'] == str(cat.id)

    @pytest.mark.asyncio
    async def test_desasignar_categoria_de_materia(self, app, db_session, setup_data):
        cat_id = _make_cat_id()
        cat = CategoriaPlus(id=cat_id, tenant_id=setup_data['tid'], codigo='DES-CAT', nombre='Categoria desasignable', activo=True)
        materia = Materia(
            tenant_id=setup_data['tid'], codigo='DES-MAT', nombre='Materia a desasignar',
            categoria_plus_id=cat_id,
        )
        db_session.add_all([cat, materia])
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['token']) as c:
            resp = await c.delete(f'/api/v1/admin/materias/{materia.id}/categoria')
        assert resp.status_code == 204

        result = await db_session.execute(
            select(Materia).where(Materia.id == materia.id)
        )
        materia_refreshed = result.scalar_one()
        assert materia_refreshed.categoria_plus_id is None

    @pytest.mark.asyncio
    async def test_get_categoria_de_materia(self, app, db_session, setup_data):
        cat_id = _make_cat_id()
        cat = CategoriaPlus(id=cat_id, tenant_id=setup_data['tid'], codigo='GET-CAT', nombre='Get categoria', activo=True)
        materia = Materia(
            tenant_id=setup_data['tid'], codigo='GET-MAT', nombre='Get materia',
            categoria_plus_id=cat_id,
        )
        db_session.add_all([cat, materia])
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['token']) as c:
            resp = await c.get(f'/api/v1/admin/materias/{materia.id}/categoria')
        assert resp.status_code == 200
        data = resp.json()
        assert data['data'] is not None
        assert data['data']['codigo'] == 'GET-CAT'

    @pytest.mark.asyncio
    async def test_get_categoria_null_si_no_tiene(self, app, db_session, setup_data):
        materia = Materia(tenant_id=setup_data['tid'], codigo='NO-CAT', nombre='Sin categoria')
        db_session.add(materia)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['token']) as c:
            resp = await c.get(f'/api/v1/admin/materias/{materia.id}/categoria')
        assert resp.status_code == 200
        assert resp.json()['data'] is None

    @pytest.mark.asyncio
    async def test_listar_materias_de_categoria(self, app, db_session, setup_data):
        cat = CategoriaPlus(tenant_id=setup_data['tid'], codigo='LIST-CAT', nombre='Listar materias', activo=True)
        db_session.add(cat)
        await db_session.flush()

        m1 = Materia(tenant_id=setup_data['tid'], codigo='M1', nombre='Materia 1', categoria_plus_id=cat.id)
        m2 = Materia(tenant_id=setup_data['tid'], codigo='M2', nombre='Materia 2', categoria_plus_id=cat.id)
        db_session.add_all([m1, m2])
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['token']) as c:
            resp = await c.get(f'/api/v1/admin/categorias-plus/{cat.id}/materias')
        assert resp.status_code == 200
        assert resp.json()['total'] == 2

    @pytest.mark.asyncio
    async def test_asignacion_masiva(self, app, db_session, setup_data):
        cat = CategoriaPlus(tenant_id=setup_data['tid'], codigo='MASIVO-CAT', nombre='Asignacion masiva', activo=True)
        db_session.add(cat)
        await db_session.flush()

        m1 = Materia(tenant_id=setup_data['tid'], codigo='M1', nombre='Materia 1')
        m2 = Materia(tenant_id=setup_data['tid'], codigo='M2', nombre='Materia 2')
        db_session.add_all([m1, m2])
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['token']) as c:
            resp = await c.post('/api/v1/admin/categorias-plus/asignacion-masiva', json={
                'categoria_plus_id': str(cat.id),
                'materia_ids': [str(m1.id), str(m2.id)],
            })
        assert resp.status_code == 200
        assert resp.json()['count'] == 2

        result = await db_session.execute(
            select(Materia).where(Materia.id == m1.id)
        )
        assert result.scalar_one().categoria_plus_id == cat.id

    @pytest.mark.asyncio
    async def test_asignacion_masiva_materia_inexistente(self, app, db_session, setup_data):
        cat = CategoriaPlus(tenant_id=setup_data['tid'], codigo='MIX-CAT', nombre='Mix', activo=True)
        db_session.add(cat)
        await db_session.flush()

        m1 = Materia(tenant_id=setup_data['tid'], codigo='M1', nombre='Materia 1')
        db_session.add(m1)
        await db_session.flush()
        fake_id = uuid.uuid4()

        async with await self._client(app, db_session, setup_data['token']) as c:
            resp = await c.post('/api/v1/admin/categorias-plus/asignacion-masiva', json={
                'categoria_plus_id': str(cat.id),
                'materia_ids': [str(m1.id), str(fake_id)],
            })
        assert resp.status_code == 200
        assert resp.json()['count'] == 1
        assert resp.json()['total_solicitado'] == 2


class TestMultiTenant:
    @pytest.mark.asyncio
    async def test_aislamiento_entre_tenants(self, app, db_session):
        tid_a = uuid.uuid4()
        tid_b = uuid.uuid4()
        tenant_a = Tenant(id=tid_a, nombre='A', codigo='TNA-CP', estado='Activo')
        tenant_b = Tenant(id=tid_b, nombre='B', codigo='TNB-CP', estado='Activo')
        db_session.add_all([tenant_a, tenant_b])
        await db_session.flush()

        cat_a = CategoriaPlus(tenant_id=tid_a, codigo='CP-A', nombre='A', activo=True)
        cat_b = CategoriaPlus(tenant_id=tid_b, codigo='CP-B', nombre='B', activo=True)
        db_session.add_all([cat_a, cat_b])
        await db_session.flush()

        role_a = Role(tenant_id=tid_a, name='ADMIN', codigo='ADMIN')
        role_b = Role(tenant_id=tid_b, name='ADMIN', codigo='ADMIN')
        db_session.add_all([role_a, role_b])
        await db_session.flush()

        perm = Permission(tenant_id=tid_a, codigo='estructura:gestionar', modulo='estructura', accion='gestionar')
        db_session.add(perm)
        perm_b = Permission(tenant_id=tid_b, codigo='estructura:gestionar', modulo='estructura', accion='gestionar')
        db_session.add(perm_b)
        await db_session.flush()

        user_a = User(tenant_id=tid_a, email='a@cp.com', password_hash='x', roles=['ADMIN'])
        db_session.add(user_a)
        await db_session.flush()
        db_session.add(RolePermission(tenant_id=tid_a, role_id=role_a.id, permiso_id=perm.id))
        db_session.add(UserRole(tenant_id=tid_a, user_id=user_a.id, role_id=role_a.id))
        await db_session.flush()
        token_a = create_access_token(str(user_a.id), str(tid_a), ['ADMIN'])

        app.dependency_overrides[get_db] = lambda: db_session
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as c:
            c.headers['Authorization'] = f'Bearer {token_a}'
            resp = await c.get('/api/v1/admin/categorias-plus')
        assert resp.status_code == 200
        data = resp.json()
        assert data['total'] == 1
        assert data['items'][0]['codigo'] == 'CP-A'

    @pytest.mark.asyncio
    async def test_misma_clave_en_distinto_tenant_ok(self, app, db_session):
        tid_a = uuid.uuid4()
        tid_b = uuid.uuid4()
        tenant_a = Tenant(id=tid_a, nombre='A', codigo='TNA2', estado='Activo')
        tenant_b = Tenant(id=tid_b, nombre='B', codigo='TNB2', estado='Activo')
        db_session.add_all([tenant_a, tenant_b])
        await db_session.flush()

        cat_a = CategoriaPlus(tenant_id=tid_a, codigo='MISMO', nombre='A', activo=True)
        cat_b = CategoriaPlus(tenant_id=tid_b, codigo='MISMO', nombre='B', activo=True)
        db_session.add_all([cat_a, cat_b])
        await db_session.flush()

        role_a = Role(tenant_id=tid_a, name='ADMIN', codigo='ADMIN')
        role_b = Role(tenant_id=tid_b, name='ADMIN', codigo='ADMIN')
        db_session.add_all([role_a, role_b])
        await db_session.flush()

        perm_a = Permission(tenant_id=tid_a, codigo='estructura:gestionar', modulo='estructura', accion='gestionar')
        perm_b = Permission(tenant_id=tid_b, codigo='estructura:gestionar', modulo='estructura', accion='gestionar')
        db_session.add_all([perm_a, perm_b])
        await db_session.flush()

        user_a = User(tenant_id=tid_a, email='a2@cp.com', password_hash='x', roles=['ADMIN'])
        db_session.add(user_a)
        await db_session.flush()
        db_session.add(RolePermission(tenant_id=tid_a, role_id=role_a.id, permiso_id=perm_a.id))
        db_session.add(UserRole(tenant_id=tid_a, user_id=user_a.id, role_id=role_a.id))
        await db_session.flush()
        token_a = create_access_token(str(user_a.id), str(tid_a), ['ADMIN'])

        app.dependency_overrides[get_db] = lambda: db_session
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as c:
            c.headers['Authorization'] = f'Bearer {token_a}'
            resp = await c.get('/api/v1/admin/categorias-plus')
        assert resp.status_code == 200
        data = resp.json()
        assert data['total'] == 1
        assert data['items'][0]['codigo'] == 'MISMO'
