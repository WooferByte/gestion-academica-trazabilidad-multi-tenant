import uuid

import pytest
import pytest_asyncio
from sqlalchemy import select

from app.core.security import create_access_token, hash_password
from app.models.mensaje import Mensaje, MensajeHilo
from app.models.tenant import Tenant
from app.models.user import User
from tests.helpers import _create_tenant, _create_user


@pytest_asyncio.fixture
async def tenant(db_session):
    return await _create_tenant(db_session)


@pytest_asyncio.fixture
async def user_a(db_session, tenant):
    u = User(
        tenant_id=tenant.id,
        email='a@test.com',
        password_hash=hash_password('pass123'),
        roles=['docente'],
    )
    db_session.add(u)
    await db_session.flush()
    return u


@pytest_asyncio.fixture
async def user_b(db_session, tenant):
    u = User(
        tenant_id=tenant.id,
        email='b@test.com',
        password_hash=hash_password('pass123'),
        roles=['docente'],
    )
    db_session.add(u)
    await db_session.flush()
    return u


@pytest_asyncio.fixture
async def user_c(db_session, tenant):
    u = User(
        tenant_id=tenant.id,
        email='c@test.com',
        password_hash=hash_password('pass123'),
        roles=['docente'],
    )
    db_session.add(u)
    await db_session.flush()
    return u


@pytest_asyncio.fixture
async def thread(db_session, tenant, user_a, user_b):
    h = MensajeHilo(
        tenant_id=tenant.id,
        participant_user_ids=[str(user_a.id), str(user_b.id)],
        subject='Consulta sobre horarios',
        last_message_at=None,
    )
    db_session.add(h)
    await db_session.flush()

    msg = Mensaje(
        tenant_id=tenant.id,
        hilo_id=h.id,
        sender_id=user_a.id,
        body='Hola, quería consultar los horarios',
    )
    db_session.add(msg)
    await db_session.flush()

    h.last_message_at = msg.created_at
    await db_session.flush()
    return h


@pytest_asyncio.fixture
async def token_a(db_session, user_a):
    return create_access_token(str(user_a.id), str(user_a.tenant_id), user_a.roles)


@pytest_asyncio.fixture
async def token_b(db_session, user_b):
    return create_access_token(str(user_b.id), str(user_b.tenant_id), user_b.roles)


@pytest_asyncio.fixture
async def token_c(db_session, user_c):
    return create_access_token(str(user_c.id), str(user_c.tenant_id), user_c.roles)


class TestListInbox:
    @pytest.mark.asyncio
    async def test_list_threads_returns_user_threads(self, async_client, thread, user_a, token_a):
        response = await async_client.get(
            '/api/v1/inbox',
            headers={'Authorization': f'Bearer {token_a}'},
        )
        assert response.status_code == 200
        data = response.json()
        assert data['total'] >= 1
        subjects = [item['subject'] for item in data['items']]
        assert 'Consulta sobre horarios' in subjects

    @pytest.mark.asyncio
    async def test_empty_inbox_returns_empty_list(self, async_client, user_c, token_c):
        response = await async_client.get(
            '/api/v1/inbox',
            headers={'Authorization': f'Bearer {token_c}'},
        )
        assert response.status_code == 200
        data = response.json()
        assert data['total'] == 0
        assert data['items'] == []

    @pytest.mark.asyncio
    async def test_unauthorized_returns_403(self, async_client):
        response = await async_client.get('/api/v1/inbox')
        assert response.status_code == 403


class TestReadThread:
    @pytest.mark.asyncio
    async def test_read_own_thread_returns_messages(self, async_client, thread, user_a, token_a):
        response = await async_client.get(
            f'/api/v1/inbox/{thread.id}',
            headers={'Authorization': f'Bearer {token_a}'},
        )
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == str(thread.id)
        assert data['subject'] == 'Consulta sobre horarios'
        assert len(data['messages']) >= 1

    @pytest.mark.asyncio
    async def test_read_other_thread_returns_404(self, async_client, thread, user_c, token_c):
        response = await async_client.get(
            f'/api/v1/inbox/{thread.id}',
            headers={'Authorization': f'Bearer {token_c}'},
        )
        assert response.status_code == 404


class TestReplyToThread:
    @pytest.mark.asyncio
    async def test_reply_to_own_thread_succeeds(self, async_client, thread, user_a, token_a):
        response = await async_client.post(
            f'/api/v1/inbox/{thread.id}/reply',
            json={'body': 'Gracias por responder'},
            headers={'Authorization': f'Bearer {token_a}'},
        )
        assert response.status_code == 200
        data = response.json()
        assert data['body'] == 'Gracias por responder'
        assert data['sender_id'] == str(user_a.id)

    @pytest.mark.asyncio
    async def test_reply_to_other_thread_returns_404(self, async_client, thread, user_c, token_c):
        response = await async_client.post(
            f'/api/v1/inbox/{thread.id}/reply',
            json={'body': 'Hola'},
            headers={'Authorization': f'Bearer {token_c}'},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_reply_empty_body_returns_422(self, async_client, thread, user_a, token_a):
        response = await async_client.post(
            f'/api/v1/inbox/{thread.id}/reply',
            json={'body': ''},
            headers={'Authorization': f'Bearer {token_a}'},
        )
        assert response.status_code == 422


class TestNewMessage:
    @pytest.mark.asyncio
    async def test_new_message_creates_thread(self, async_client, user_a, user_b, token_a):
        response = await async_client.post(
            '/api/v1/inbox',
            json={
                'recipient_id': str(user_b.id),
                'subject': 'Nueva consulta',
                'body': 'Hola, necesito información',
            },
            headers={'Authorization': f'Bearer {token_a}'},
        )
        assert response.status_code == 201
        data = response.json()
        assert data['subject'] == 'Nueva consulta'
        assert 'messages' in data
        assert len(data['messages']) == 1

    @pytest.mark.asyncio
    async def test_new_message_recipient_not_found_returns_404(self, async_client, user_a, token_a):
        fake_id = uuid.uuid4()
        response = await async_client.post(
            '/api/v1/inbox',
            json={
                'recipient_id': str(fake_id),
                'subject': 'Test',
                'body': 'Hola',
            },
            headers={'Authorization': f'Bearer {token_a}'},
        )
        assert response.status_code == 404


class TestMultiTenantIsolation:
    @pytest.mark.asyncio
    async def test_cross_tenant_user_not_visible(self, db_session, async_client, tenant, user_a, token_a):
        tenant_b = Tenant(nombre='Other', codigo='OTH')
        db_session.add(tenant_b)
        await db_session.flush()

        other_user = User(
            tenant_id=tenant_b.id,
            email='other@test.com',
            password_hash=hash_password('pass'),
            roles=['docente'],
        )
        db_session.add(other_user)
        await db_session.flush()

        response = await async_client.post(
            '/api/v1/inbox',
            json={
                'recipient_id': str(other_user.id),
                'subject': 'Cross tenant',
                'body': 'Hola',
            },
            headers={'Authorization': f'Bearer {token_a}'},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_inbox_isolation(self, db_session, async_client, tenant, user_a, token_a):
        tenant_b = Tenant(nombre='Other2', codigo='OTH2')
        db_session.add(tenant_b)
        await db_session.flush()

        other_user = User(
            tenant_id=tenant_b.id,
            email='other2@test.com',
            password_hash=hash_password('pass'),
            roles=['docente'],
        )
        db_session.add(other_user)
        await db_session.flush()

        hilo_b = MensajeHilo(
            tenant_id=tenant_b.id,
            participant_user_ids=[str(other_user.id), str(uuid.uuid4())],
            subject='Thread in other tenant',
        )
        db_session.add(hilo_b)
        await db_session.flush()

        response = await async_client.get(
            '/api/v1/inbox',
            headers={'Authorization': f'Bearer {token_a}'},
        )
        assert response.status_code == 200
        data = response.json()
        subjects = [item['subject'] for item in data['items']]
        assert 'Thread in other tenant' not in subjects
