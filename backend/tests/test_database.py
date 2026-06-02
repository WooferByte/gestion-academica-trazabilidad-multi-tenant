import pytest
from sqlalchemy import text

from app.core.dependencies import get_db


@pytest.mark.asyncio
async def test_db_select_one(db_session):
    result = await db_session.execute(text('SELECT 1'))
    value = result.scalar()
    assert value == 1


@pytest.mark.asyncio
async def test_db_connection_follows_session_per_request_pattern():
    gen1 = get_db()
    gen2 = get_db()
    s1 = await gen1.__anext__()
    s2 = await gen2.__anext__()
    assert s1 is not s2
    await gen1.aclose()
    await gen2.aclose()


@pytest.mark.asyncio
async def test_session_closes_on_exception():
    gen = get_db()
    session = await gen.__anext__()

    with pytest.raises(RuntimeError):
        async with session.begin():
            raise RuntimeError('test rollback')

    await gen.aclose()
    with pytest.raises(Exception):
        await session.execute(text('SELECT 1'))
