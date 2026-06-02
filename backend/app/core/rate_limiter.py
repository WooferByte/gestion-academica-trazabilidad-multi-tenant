from collections import defaultdict
from datetime import datetime, timedelta, timezone


class LoginRateLimiter:
    def __init__(self, max_attempts: int = 5, window_seconds: int = 60):
        self._max_attempts = max_attempts
        self._window_seconds = window_seconds
        self._attempts: dict[str, list[datetime]] = defaultdict(list)

    def check(self, ip: str, email: str) -> bool:
        key = f'{ip}:{email}'
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=self._window_seconds)
        self._attempts[key] = [
            t for t in self._attempts[key] if t > window_start
        ]
        return len(self._attempts[key]) < self._max_attempts

    def record(self, ip: str, email: str) -> None:
        key = f'{ip}:{email}'
        self._attempts[key].append(datetime.now(timezone.utc))

    def remaining(self, ip: str, email: str) -> int:
        key = f'{ip}:{email}'
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=self._window_seconds)
        self._attempts[key] = [
            t for t in self._attempts[key] if t > window_start
        ]
        remaining = self._max_attempts - len(self._attempts[key])
        return max(0, remaining)
