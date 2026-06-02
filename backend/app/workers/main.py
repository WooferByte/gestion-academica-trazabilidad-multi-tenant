# Entrypoint mínimo del worker de comunicaciones.
# RESERVADO — la tecnología de cola (asyncio/Celery/ARQ) se define en ADR-003.
# Por ahora: loop no-op que mantiene el proceso vivo.
#
# Uso:
#   python -m app.workers.main

import asyncio
import logging

logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info('Worker started (placeholder)')
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logger.info('Worker shutting down')


if __name__ == '__main__':
    asyncio.run(main())
