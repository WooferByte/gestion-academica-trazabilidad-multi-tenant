import asyncio
import os
import sys
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import Settings
from app.core.database import Base, get_session_factory, init_engine
from app.core.dependencies import get_db
from app.main import create_app
from app.models.user import User, RefreshToken, PasswordResetToken
from app.models.role import Role
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.models.user_role import UserRole
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from tests.helpers import TestModel

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    from app.api.v1.routers.auth import reset_rate_limiter
    reset_rate_limiter()
    return


@pytest.fixture(autouse=True)
def clean_env():
    saved = {
        'DATABASE_URL': os.environ.get('DATABASE_URL'),
        'SECRET_KEY': os.environ.get('SECRET_KEY'),
        'ENCRYPTION_KEY': os.environ.get('ENCRYPTION_KEY'),
    }
    yield
    for key, value in saved.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


@pytest_asyncio.fixture(autouse=True)
async def setup_tables():
    """Create all tables before each test, drop after."""
    settings = Settings()
    dsn = str(settings.database_url)
    engine = create_async_engine(dsn, isolation_level='AUTOCOMMIT')
    async with engine.connect() as conn:
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(setup_tables) -> AsyncGenerator[AsyncSession, None]:
    init_engine(str(Settings().database_url))
    async with get_session_factory()() as session:
        yield session


@pytest.fixture
def app():
    return create_app()


@pytest_asyncio.fixture
async def async_client(db_session) -> AsyncGenerator[AsyncClient, None]:
    application = create_app()
    application.dependency_overrides[get_db] = lambda: db_session
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        yield client
