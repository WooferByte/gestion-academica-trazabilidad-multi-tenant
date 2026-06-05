import pytest
import pytest_asyncio

from app.core.security import decrypt, encrypt, hash_password, verify_password
from app.models.tenant import Tenant
from app.models.user import User
from app.repositories.user_repository import UserRepository


@pytest_asyncio.fixture
async def tenant(db_session):
    t = Tenant(nombre='Test Tenant', codigo='TT')
    db_session.add(t)
    await db_session.flush()
    return t


@pytest_asyncio.fixture
async def user_repo(db_session, tenant):
    return UserRepository(session=db_session, tenant_id=tenant.id)


class TestUserModel:
    @pytest.mark.asyncio
    async def test_create_user_with_all_fields(self, user_repo, tenant):
        user = await user_repo.create(
            email='juan@test.com',
            password_hash=hash_password('pass123'),
            nombre_cifrado=encrypt('Juan'),
            apellido_cifrado=encrypt('Pérez'),
            dni_cifrado=encrypt('12345678'),
            roles=['admin'],
            is_active=True,
        )
        assert user.id is not None
        assert user.email == 'juan@test.com'
        assert user.password_hash.startswith('$argon2id$')
        assert verify_password('pass123', user.password_hash) is True
        assert decrypt(user.nombre_cifrado) == 'Juan'
        assert decrypt(user.apellido_cifrado) == 'Pérez'
        assert decrypt(user.dni_cifrado) == '12345678'
        assert user.roles == ['admin']
        assert user.is_active is True
        assert user.tenant_id == tenant.id
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.deleted_at is None

    @pytest.mark.asyncio
    async def test_email_unique_per_tenant(self, user_repo):
        await user_repo.create(
            email='duplicate@test.com',
            password_hash=hash_password('pass123'),
        )
        with pytest.raises(Exception):
            await user_repo.create(
                email='duplicate@test.com',
                password_hash=hash_password('pass456'),
            )

    @pytest.mark.asyncio
    async def test_same_email_different_tenants(self, db_session, tenant, user_repo):
        tenant_b = Tenant(nombre='Tenant B', codigo='TB')
        db_session.add(tenant_b)
        await db_session.flush()

        repo_b = UserRepository(session=db_session, tenant_id=tenant_b.id)

        await user_repo.create(
            email='comun@test.com',
            password_hash=hash_password('pass123'),
        )
        user_b = await repo_b.create(
            email='comun@test.com',
            password_hash=hash_password('pass456'),
        )
        assert user_b is not None
        assert user_b.tenant_id == tenant_b.id

    @pytest.mark.asyncio
    async def test_soft_delete_user(self, user_repo):
        user = await user_repo.create(
            email='delete@test.com',
            password_hash=hash_password('pass123'),
        )
        assert user.deleted_at is None

        await user_repo.soft_delete(user)
        assert user.deleted_at is not None

        found = await user_repo.get(user.id)
        assert found is None

    @pytest.mark.asyncio
    async def test_pii_fields_encrypted_at_rest(self, user_repo):
        nombre_plain = 'Juan'
        apellido_plain = 'Pérez'

        user = await user_repo.create(
            email='pii@test.com',
            password_hash=hash_password('pass123'),
            nombre_cifrado=encrypt(nombre_plain),
            apellido_cifrado=encrypt(apellido_plain),
        )
        assert user.nombre_cifrado != nombre_plain
        assert user.apellido_cifrado != apellido_plain
        assert decrypt(user.nombre_cifrado) == nombre_plain
        assert decrypt(user.apellido_cifrado) == apellido_plain

    @pytest.mark.asyncio
    async def test_default_roles_empty_list(self, user_repo):
        user = await user_repo.create(
            email='noroles@test.com',
            password_hash=hash_password('pass123'),
        )
        assert user.roles == []

    @pytest.mark.asyncio
    async def test_default_is_active_true(self, user_repo):
        user = await user_repo.create(
            email='active@test.com',
            password_hash=hash_password('pass123'),
        )
        assert user.is_active is True
