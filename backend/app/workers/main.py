import asyncio
import logging
import os
import signal
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session_factory, init_engine
from app.core.config import Settings
from app.models.comunicacion import Comunicacion, EstadoComunicacion
from app.repositories.comunicacion_repository import ComunicacionRepository

logger = logging.getLogger(__name__)

POLL_INTERVAL = int(os.environ.get('WORKER_POLL_INTERVAL', '30'))
BATCH_SIZE = int(os.environ.get('WORKER_BATCH_SIZE', '50'))

_shutdown_event = asyncio.Event()


def _handle_signal() -> None:
    _shutdown_event.set()


async def _send_email(comunicacion: Comunicacion) -> None:
    await asyncio.sleep(0.1)


async def _process_batch(session: AsyncSession | None = None) -> int:
    if session is not None:
        return await _process_batch_with_session(session)
    async with get_session_factory()() as s:
        result = await _process_batch_with_session(s)
        await s.commit()
        return result


async def _process_batch_with_session(session: AsyncSession) -> int:
    result = await session.execute(
        select(Comunicacion)
        .where(Comunicacion.deleted_at.is_(None))
        .where(Comunicacion.estado == EstadoComunicacion.PENDIENTE)
        .where(
            (Comunicacion.programada_para.is_(None))
            | (Comunicacion.programada_para <= datetime.now(timezone.utc))
        )
        .limit(BATCH_SIZE)
    )
    comunicaciones = result.scalars().all()
    if not comunicaciones:
        return 0

    ids = [c.id for c in comunicaciones]
    await session.execute(
        update(Comunicacion)
        .where(Comunicacion.id.in_(ids))
        .where(Comunicacion.estado == EstadoComunicacion.PENDIENTE)
        .values(estado=EstadoComunicacion.ENVIANDO)
    )
    await session.flush()

    for c in comunicaciones:
        try:
            await _send_email(c)
            await session.execute(
                update(Comunicacion)
                .where(Comunicacion.id == c.id)
                .values(
                    estado=EstadoComunicacion.ENVIADO,
                    enviada_at=datetime.now(timezone.utc),
                )
            )
        except Exception as exc:
            logger.exception('Error enviando comunicación %s', c.id)
            await session.execute(
                update(Comunicacion)
                .where(Comunicacion.id == c.id)
                .values(
                    estado=EstadoComunicacion.ERROR,
                    error_msg=str(exc),
                )
            )

    await session.flush()
    return len(comunicaciones)


async def main() -> None:
    logger.info('Worker started (poll_interval=%ds, batch_size=%d)', POLL_INTERVAL, BATCH_SIZE)
    settings = Settings()
    init_engine(str(settings.database_url))

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, _handle_signal)
        except NotImplementedError:
            pass

    try:
        while not _shutdown_event.is_set():
            try:
                processed = await _process_batch()
                if processed:
                    logger.info('Procesadas %d comunicaciones', processed)
            except Exception as exc:
                logger.exception('Error en ciclo de worker: %s', exc)

            try:
                await asyncio.wait_for(
                    _shutdown_event.wait(),
                    timeout=POLL_INTERVAL,
                )
                break
            except asyncio.TimeoutError:
                continue
    finally:
        from app.core.database import dispose_engine
        await dispose_engine()
        logger.info('Worker shut down')


if __name__ == '__main__':
    asyncio.run(main())
