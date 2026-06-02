from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import Settings


class Base(DeclarativeBase):
    pass


_engine = None  # type: ignore
_session_factory = None  # type: ignore


def init_engine(database_url: str, echo: bool = False) -> None:
    global _engine, _session_factory
    _engine = create_async_engine(
        database_url,
        echo=echo,
        pool_size=10,
        max_overflow=20,
    )
    _session_factory = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def dispose_engine() -> None:
    if _engine is not None:
        await _engine.dispose()


def get_session_factory():
    if _session_factory is None:
        settings = Settings()
        init_engine(str(settings.database_url))
    return _session_factory
