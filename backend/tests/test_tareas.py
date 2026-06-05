import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.security import create_access_token
from app.main import create_app
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.tarea import ComentarioTarea, Tarea
from app.models.tenant import Tenant
from app.models.user import User
from app.models.user_role import UserRole
from app.models.materia import Materia


@pytest_asyncio.fixture
async def setup_data(db_session):
    tid = uuid.uuid4()
    tenant = Tenant(id=tid, nombre='Test', codigo='TST-TAR', estado='Activo')
    db_session.add(tenant)

    admin = User(tenant_id=tid, email='admin@t.com', password_hash='x', roles=['ADMIN'])
    db_session.add(admin)
    profe = User(tenant_id=tid, email='profe@t.com', password_hash='x', roles=['PROFESOR'])
    db_session.add(profe)
    tutor = User(tenant_id=tid, email='tutor@t.com', password_hash='x', roles=['TUTOR'])
    db_session.add(tutor)
    alumno = User(tenant_id=tid, email='alumno@t.com', password_hash='x', roles=['ALUMNO'])
    db_session.add(alumno)
    await db_session.flush()

    materia = Materia(tenant_id=tid, codigo='MAT-TAR', nombre='Test Materia Tareas')
    db_session.add(materia)
    await db_session.flush()

    role_admin = Role(tenant_id=tid, name='ADMIN', codigo='ADMIN')
    db_session.add(role_admin)
    await db_session.flush()
    perm = Permission(tenant_id=tid, codigo='tareas:gestionar', modulo='tareas', accion='gestionar')
    db_session.add(perm)
    await db_session.flush()
    db_session.add(RolePermission(tenant_id=tid, role_id=role_admin.id, permiso_id=perm.id))
    db_session.add(UserRole(tenant_id=tid, user_id=admin.id, role_id=role_admin.id))
    await db_session.flush()

    admin_token = create_access_token(str(admin.id), str(tid), ['ADMIN'])
    profe_token = create_access_token(str(profe.id), str(tid), ['PROFESOR'])
    tutor_token = create_access_token(str(tutor.id), str(tid), ['TUTOR'])
    alumno_token = create_access_token(str(alumno.id), str(tid), ['ALUMNO'])

    return {
        'tid': tid,
        'admin': admin, 'profe': profe, 'tutor': tutor, 'alumno': alumno,
        'admin_token': admin_token, 'profe_token': profe_token,
        'tutor_token': tutor_token, 'alumno_token': alumno_token,
        'materia': materia,
    }


class TestTareas:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        c = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        c.headers['Authorization'] = f'Bearer {token}'
        return c

    @pytest.mark.asyncio
    async def test_crear_tarea_201(self, app, db_session, setup_data):
        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.post('/api/v1/tareas', json={
                'asignado_a': str(setup_data['profe'].id),
                'descripcion': 'Preparar material para la clase',
            })
        assert resp.status_code == 201
        data = resp.json()
        assert data['descripcion'] == 'Preparar material para la clase'
        assert data['asignado_a'] == str(setup_data['profe'].id)
        assert data['asignado_por'] == str(setup_data['admin'].id)
        assert data['estado'] == 'Pendiente'
        assert data['tenant_id'] == str(setup_data['tid'])

    @pytest.mark.asyncio
    async def test_crear_tarea_con_materia(self, app, db_session, setup_data):
        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.post('/api/v1/tareas', json={
                'asignado_a': str(setup_data['profe'].id),
                'descripcion': 'Corregir parciales',
                'materia_id': str(setup_data['materia'].id),
            })
        assert resp.status_code == 201
        data = resp.json()
        assert data['materia_id'] == str(setup_data['materia'].id)

    @pytest.mark.asyncio
    async def test_crear_tarea_con_contexto(self, app, db_session, setup_data):
        ctx_id = str(uuid.uuid4())
        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.post('/api/v1/tareas', json={
                'asignado_a': str(setup_data['profe'].id),
                'descripcion': 'Tarea con contexto',
                'contexto_id': ctx_id,
            })
        assert resp.status_code == 201
        assert resp.json()['contexto_id'] == ctx_id

    @pytest.mark.asyncio
    async def test_403_sin_permiso(self, app, db_session, setup_data):
        async with await self._client(app, db_session, setup_data['alumno_token']) as c:
            resp = await c.post('/api/v1/tareas', json={
                'asignado_a': str(setup_data['profe'].id),
                'descripcion': 'No autorizado',
            })
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_422_campo_extra(self, app, db_session, setup_data):
        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.post('/api/v1/tareas', json={
                'asignado_a': str(setup_data['profe'].id),
                'descripcion': 'Test',
                'campo_extra': 'no_permitido',
            })
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_400_usuario_inexistente(self, app, db_session, setup_data):
        fake_id = str(uuid.uuid4())
        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.post('/api/v1/tareas', json={
                'asignado_a': fake_id,
                'descripcion': 'Usuario no existe',
            })
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_mis_tareas_sin_permiso(self, app, db_session, setup_data):
        async with await self._client(app, db_session, setup_data['alumno_token']) as c:
            resp = await c.get('/api/v1/tareas/mis-tareas')
        assert resp.status_code == 200
        assert resp.json()['total'] == 0

    @pytest.mark.asyncio
    async def test_mis_tareas_con_asignaciones(self, app, db_session, setup_data):
        t1 = Tarea(
            tenant_id=setup_data['tid'], asignado_a=setup_data['profe'].id,
            asignado_por=setup_data['admin'].id, descripcion='Tarea 1',
        )
        t2 = Tarea(
            tenant_id=setup_data['tid'], asignado_a=setup_data['profe'].id,
            asignado_por=setup_data['admin'].id, descripcion='Tarea 2',
        )
        t3 = Tarea(
            tenant_id=setup_data['tid'], asignado_a=setup_data['admin'].id,
            asignado_por=setup_data['admin'].id, descripcion='Tarea de admin',
        )
        db_session.add_all([t1, t2, t3])
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['profe_token']) as c:
            resp = await c.get('/api/v1/tareas/mis-tareas')
        assert resp.status_code == 200
        data = resp.json()
        assert data['total'] == 2
        descs = [i['descripcion'] for i in data['items']]
        assert 'Tarea 1' in descs
        assert 'Tarea 2' in descs
        assert 'Tarea de admin' not in descs

    @pytest.mark.asyncio
    async def test_mis_tareas_filtro_estado(self, app, db_session, setup_data):
        db_session.add(Tarea(
            tenant_id=setup_data['tid'], asignado_a=setup_data['profe'].id,
            asignado_por=setup_data['admin'].id, descripcion='Pendiente',
        ))
        db_session.add(Tarea(
            tenant_id=setup_data['tid'], asignado_a=setup_data['profe'].id,
            asignado_por=setup_data['admin'].id, descripcion='En progreso',
            estado='En progreso',
        ))
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['profe_token']) as c:
            resp = await c.get('/api/v1/tareas/mis-tareas?estado=Pendiente')
        assert resp.status_code == 200
        data = resp.json()
        assert data['total'] == 1
        assert data['items'][0]['descripcion'] == 'Pendiente'

    @pytest.mark.asyncio
    async def test_obtener_tarea(self, app, db_session, setup_data):
        tarea = Tarea(
            tenant_id=setup_data['tid'], asignado_a=setup_data['profe'].id,
            asignado_por=setup_data['admin'].id, descripcion='Ver detalle',
        )
        db_session.add(tarea)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.get(f'/api/v1/tareas/{tarea.id}')
        assert resp.status_code == 200
        assert resp.json()['descripcion'] == 'Ver detalle'

    @pytest.mark.asyncio
    async def test_obtener_tarea_404(self, app, db_session, setup_data):
        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.get(f'/api/v1/tareas/{uuid.uuid4()}')
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_actualizar_tarea(self, app, db_session, setup_data):
        tarea = Tarea(
            tenant_id=setup_data['tid'], asignado_a=setup_data['profe'].id,
            asignado_por=setup_data['admin'].id, descripcion='Original',
        )
        db_session.add(tarea)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.patch(f'/api/v1/tareas/{tarea.id}', json={
                'descripcion': 'Actualizada',
            })
        assert resp.status_code == 200
        assert resp.json()['descripcion'] == 'Actualizada'

    @pytest.mark.asyncio
    async def test_cambiar_estado_valido(self, app, db_session, setup_data):
        tarea = Tarea(
            tenant_id=setup_data['tid'], asignado_a=setup_data['profe'].id,
            asignado_por=setup_data['admin'].id, descripcion='Cambio estado',
        )
        db_session.add(tarea)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.patch(f'/api/v1/tareas/{tarea.id}/estado', json={
                'estado': 'En progreso',
            })
        assert resp.status_code == 200
        assert resp.json()['estado'] == 'En progreso'

    @pytest.mark.asyncio
    async def test_cambiar_estado_invalido(self, app, db_session, setup_data):
        tarea = Tarea(
            tenant_id=setup_data['tid'], asignado_a=setup_data['profe'].id,
            asignado_por=setup_data['admin'].id, descripcion='Salto invalido',
        )
        db_session.add(tarea)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.patch(f'/api/v1/tareas/{tarea.id}/estado', json={
                'estado': 'Resuelta',
            })
        assert resp.status_code == 400
        assert 'Transición no permitida' in resp.json()['detail']

    @pytest.mark.asyncio
    async def test_cancelar_tarea(self, app, db_session, setup_data):
        tarea = Tarea(
            tenant_id=setup_data['tid'], asignado_a=setup_data['profe'].id,
            asignado_por=setup_data['admin'].id, descripcion='A cancelar',
        )
        db_session.add(tarea)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.patch(f'/api/v1/tareas/{tarea.id}/estado', json={
                'estado': 'Cancelada',
            })
        assert resp.status_code == 200
        assert resp.json()['estado'] == 'Cancelada'

    @pytest.mark.asyncio
    async def test_cancelada_no_vuelve(self, app, db_session, setup_data):
        tarea = Tarea(
            tenant_id=setup_data['tid'], asignado_a=setup_data['profe'].id,
            asignado_por=setup_data['admin'].id, descripcion='Cancelada',
            estado='Cancelada',
        )
        db_session.add(tarea)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.patch(f'/api/v1/tareas/{tarea.id}/estado', json={
                'estado': 'Pendiente',
            })
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_cambiar_estado_404(self, app, db_session, setup_data):
        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.patch(f'/api/v1/tareas/{uuid.uuid4()}/estado', json={
                'estado': 'En progreso',
            })
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_estado_invalido(self, app, db_session, setup_data):
        tarea = Tarea(
            tenant_id=setup_data['tid'], asignado_a=setup_data['profe'].id,
            asignado_por=setup_data['admin'].id, descripcion='Estado raro',
        )
        db_session.add(tarea)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.patch(f'/api/v1/tareas/{tarea.id}/estado', json={
                'estado': 'Inexistente',
            })
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_soft_delete(self, app, db_session, setup_data):
        tarea = Tarea(
            tenant_id=setup_data['tid'], asignado_a=setup_data['profe'].id,
            asignado_por=setup_data['admin'].id, descripcion='A borrar',
        )
        db_session.add(tarea)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.delete(f'/api/v1/tareas/{tarea.id}')
        assert resp.status_code == 200
        assert resp.json()['detalle'] == 'Tarea eliminada'

        result = await db_session.execute(
            select(Tarea).where(Tarea.id == tarea.id)
        )
        deleted = result.scalar_one()
        assert deleted.deleted_at is not None

    @pytest.mark.asyncio
    async def test_soft_delete_404(self, app, db_session, setup_data):
        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.delete(f'/api/v1/tareas/{uuid.uuid4()}')
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_agregar_comentario(self, app, db_session, setup_data):
        tarea = Tarea(
            tenant_id=setup_data['tid'], asignado_a=setup_data['profe'].id,
            asignado_por=setup_data['admin'].id, descripcion='Con comentario',
        )
        db_session.add(tarea)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.post(f'/api/v1/tareas/{tarea.id}/comentarios', json={
                'texto': 'Este es un comentario de prueba',
            })
        assert resp.status_code == 201
        data = resp.json()
        assert data['texto'] == 'Este es un comentario de prueba'
        assert data['tarea_id'] == str(tarea.id)
        assert data['autor_id'] == str(setup_data['admin'].id)

    @pytest.mark.asyncio
    async def test_comentario_en_respuesta_tarea(self, app, db_session, setup_data):
        tarea = Tarea(
            tenant_id=setup_data['tid'], asignado_a=setup_data['profe'].id,
            asignado_por=setup_data['admin'].id, descripcion='Tarea con comentarios',
        )
        db_session.add(tarea)
        await db_session.flush()

        comentario = ComentarioTarea(
            tenant_id=setup_data['tid'], tarea_id=tarea.id,
            autor_id=setup_data['admin'].id, texto='Comentario inicial',
            creado_at=datetime.now(timezone.utc),
        )
        db_session.add(comentario)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.get(f'/api/v1/tareas/{tarea.id}')
        assert resp.status_code == 200
        data = resp.json()
        assert len(data['comentarios']) == 1
        assert data['comentarios'][0]['texto'] == 'Comentario inicial'

    @pytest.mark.asyncio
    async def test_admin_listar_todas(self, app, db_session, setup_data):
        db_session.add_all([
            Tarea(tenant_id=setup_data['tid'], asignado_a=setup_data['profe'].id,
                  asignado_por=setup_data['admin'].id, descripcion='Admin 1'),
            Tarea(tenant_id=setup_data['tid'], asignado_a=setup_data['tutor'].id,
                  asignado_por=setup_data['admin'].id, descripcion='Admin 2'),
        ])
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.get('/api/v1/admin/tareas')
        assert resp.status_code == 200
        data = resp.json()
        assert data['total'] == 2

    @pytest.mark.asyncio
    async def test_admin_filtros(self, app, db_session, setup_data):
        t1 = Tarea(tenant_id=setup_data['tid'], asignado_a=setup_data['profe'].id,
                   asignado_por=setup_data['admin'].id, descripcion='Para profe',
                   materia_id=setup_data['materia'].id)
        db_session.add(t1)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.get(
                f'/api/v1/admin/tareas?asignado_a={setup_data["profe"].id}'
                f'&materia_id={setup_data["materia"].id}'
            )
        assert resp.status_code == 200
        assert resp.json()['total'] == 1

    @pytest.mark.asyncio
    async def test_admin_search(self, app, db_session, setup_data):
        db_session.add(Tarea(
            tenant_id=setup_data['tid'], asignado_a=setup_data['profe'].id,
            asignado_por=setup_data['admin'].id, descripcion='Buscar esta tarea',
        ))
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.get('/api/v1/admin/tareas?search=Buscar')
        assert resp.status_code == 200
        assert resp.json()['total'] == 1

    @pytest.mark.asyncio
    async def test_actualizar_asignado_a(self, app, db_session, setup_data):
        tarea = Tarea(
            tenant_id=setup_data['tid'], asignado_a=setup_data['profe'].id,
            asignado_por=setup_data['admin'].id, descripcion='Reasignar',
        )
        db_session.add(tarea)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.patch(f'/api/v1/tareas/{tarea.id}', json={
                'asignado_a': str(setup_data['tutor'].id),
            })
        assert resp.status_code == 200
        assert resp.json()['asignado_a'] == str(setup_data['tutor'].id)

    @pytest.mark.asyncio
    async def test_multi_tenant_aislamiento(self, app, db_session):
        tid_a = uuid.uuid4()
        tid_b = uuid.uuid4()
        tenant_a = Tenant(id=tid_a, nombre='A', codigo='TNA-TAR', estado='Activo')
        tenant_b = Tenant(id=tid_b, nombre='B', codigo='TNB-TAR', estado='Activo')
        db_session.add_all([tenant_a, tenant_b])
        await db_session.flush()

        admin_a = User(tenant_id=tid_a, email='admin_a@t.com', password_hash='x', roles=['ADMIN'])
        db_session.add(admin_a)
        profe_a = User(tenant_id=tid_a, email='profe_a@t.com', password_hash='x', roles=['PROFESOR'])
        db_session.add(profe_a)
        await db_session.flush()

        role_a = Role(tenant_id=tid_a, name='ADMIN', codigo='ADMIN')
        db_session.add(role_a)
        await db_session.flush()
        perm_a = Permission(tenant_id=tid_a, codigo='tareas:gestionar', modulo='tareas', accion='gestionar')
        db_session.add(perm_a)
        await db_session.flush()
        db_session.add(RolePermission(tenant_id=tid_a, role_id=role_a.id, permiso_id=perm_a.id))
        db_session.add(UserRole(tenant_id=tid_a, user_id=admin_a.id, role_id=role_a.id))
        await db_session.flush()

        tarea_a = Tarea(
            tenant_id=tid_a, asignado_a=profe_a.id,
            asignado_por=admin_a.id, descripcion='Solo tenant A',
        )
        db_session.add(tarea_a)
        await db_session.flush()

        token_a = create_access_token(str(admin_a.id), str(tid_a), ['ADMIN'])

        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as c:
            c.headers['Authorization'] = f'Bearer {token_a}'
            app.dependency_overrides[get_db] = lambda: db_session
            resp = await c.get('/api/v1/admin/tareas')
        assert resp.status_code == 200
        descs = [i['descripcion'] for i in resp.json()['items']]
        assert 'Solo tenant A' in descs
        for item in resp.json()['items']:
            assert item['tenant_id'] == str(tid_a)


class TestTransicionesEstado:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        c = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        c.headers['Authorization'] = f'Bearer {token}'
        return c

    @pytest.mark.asyncio
    async def test_pendiente_a_en_progreso(self, app, db_session, setup_data):
        tarea = Tarea(tenant_id=setup_data['tid'], asignado_a=setup_data['profe'].id,
                      asignado_por=setup_data['admin'].id, descripcion='P→EP')
        db_session.add(tarea)
        await db_session.flush()
        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.patch(f'/api/v1/tareas/{tarea.id}/estado', json={'estado': 'En progreso'})
        assert resp.status_code == 200
        assert resp.json()['estado'] == 'En progreso'

    @pytest.mark.asyncio
    async def test_pendiente_a_cancelada(self, app, db_session, setup_data):
        tarea = Tarea(tenant_id=setup_data['tid'], asignado_a=setup_data['profe'].id,
                      asignado_por=setup_data['admin'].id, descripcion='P→C')
        db_session.add(tarea)
        await db_session.flush()
        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.patch(f'/api/v1/tareas/{tarea.id}/estado', json={'estado': 'Cancelada'})
        assert resp.status_code == 200
        assert resp.json()['estado'] == 'Cancelada'

    @pytest.mark.asyncio
    async def test_en_progreso_a_resuelta(self, app, db_session, setup_data):
        tarea = Tarea(tenant_id=setup_data['tid'], asignado_a=setup_data['profe'].id,
                      asignado_por=setup_data['admin'].id, descripcion='EP→R',
                      estado='En progreso')
        db_session.add(tarea)
        await db_session.flush()
        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.patch(f'/api/v1/tareas/{tarea.id}/estado', json={'estado': 'Resuelta'})
        assert resp.status_code == 200
        assert resp.json()['estado'] == 'Resuelta'

    @pytest.mark.asyncio
    async def test_en_progreso_a_cancelada(self, app, db_session, setup_data):
        tarea = Tarea(tenant_id=setup_data['tid'], asignado_a=setup_data['profe'].id,
                      asignado_por=setup_data['admin'].id, descripcion='EP→C',
                      estado='En progreso')
        db_session.add(tarea)
        await db_session.flush()
        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.patch(f'/api/v1/tareas/{tarea.id}/estado', json={'estado': 'Cancelada'})
        assert resp.status_code == 200
        assert resp.json()['estado'] == 'Cancelada'

    @pytest.mark.asyncio
    async def test_resuelta_no_cambia(self, app, db_session, setup_data):
        tarea = Tarea(tenant_id=setup_data['tid'], asignado_a=setup_data['profe'].id,
                      asignado_por=setup_data['admin'].id, descripcion='R→X',
                      estado='Resuelta')
        db_session.add(tarea)
        await db_session.flush()
        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.patch(f'/api/v1/tareas/{tarea.id}/estado', json={'estado': 'En progreso'})
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_cancelada_no_cambia(self, app, db_session, setup_data):
        tarea = Tarea(tenant_id=setup_data['tid'], asignado_a=setup_data['profe'].id,
                      asignado_por=setup_data['admin'].id, descripcion='C→X',
                      estado='Cancelada')
        db_session.add(tarea)
        await db_session.flush()
        async with await self._client(app, db_session, setup_data['admin_token']) as c:
            resp = await c.patch(f'/api/v1/tareas/{tarea.id}/estado', json={'estado': 'En progreso'})
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_flujo_completo(self, app, db_session, setup_data):
        tarea = Tarea(tenant_id=setup_data['tid'], asignado_a=setup_data['profe'].id,
                      asignado_por=setup_data['admin'].id, descripcion='Flujo completo')
        db_session.add(tarea)
        await db_session.flush()

        c = await self._client(app, db_session, setup_data['admin_token'])
        async with c:
            # Pendiente → En progreso
            r1 = await c.patch(f'/api/v1/tareas/{tarea.id}/estado', json={'estado': 'En progreso'})
            assert r1.status_code == 200
            assert r1.json()['estado'] == 'En progreso'

            # En progreso → Resuelta
            r2 = await c.patch(f'/api/v1/tareas/{tarea.id}/estado', json={'estado': 'Resuelta'})
            assert r2.status_code == 200
            assert r2.json()['estado'] == 'Resuelta'
