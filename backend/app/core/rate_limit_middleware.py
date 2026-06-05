import logging
import time
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        max_requests: int = 100,
        window_seconds: int = 60,
    ) -> None:
        super().__init__(app)
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def _cleanup_key(self, key: str, now: float) -> None:
        """Remove expired timestamps and delete key if empty."""
        if key not in self._requests:
            return
        window_start = now - self._window_seconds
        timestamps = self._requests[key]
        self._requests[key] = [t for t in timestamps if t >= window_start]
        if not self._requests[key]:
            del self._requests[key]

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.url.path.rstrip('/') == '/health':
            return await call_next(request)

        client_ip = request.client.host if request.client else 'unknown'
        key = f'{client_ip}:{request.url.path}'
        now = time.time()

        self._cleanup_key(key, now)

        if len(self._requests.get(key, [])) >= self._max_requests:
            oldest = self._requests[key][0]
            retry_after = int(oldest + self._window_seconds - now)
            reset_time = int(oldest + self._window_seconds)
            logger.warning(
                'Rate limit exceeded',
                extra={
                    'client_ip': client_ip,
                    'path': request.url.path,
                    'key': key,
                    'max_requests': self._max_requests,
                    'retry_after': retry_after,
                },
            )
            return Response(
                status_code=429,
                content='{"detail": "Too Many Requests"}',
                media_type='application/json',
                headers={
                    'Retry-After': str(max(retry_after, 1)),
                    'X-RateLimit-Limit': str(self._max_requests),
                    'X-RateLimit-Remaining': '0',
                    'X-RateLimit-Reset': str(reset_time),
                },
            )

        self._requests[key].append(now)

        response = await call_next(request)

        remaining = max(0, self._max_requests - len(self._requests[key]))
        response.headers['X-RateLimit-Limit'] = str(self._max_requests)
        response.headers['X-RateLimit-Remaining'] = str(remaining)
        if self._requests.get(key):
            reset_time = int(self._requests[key][0] + self._window_seconds)
        else:
            reset_time = int(now + self._window_seconds)
        response.headers['X-RateLimit-Reset'] = str(reset_time)

        return response
