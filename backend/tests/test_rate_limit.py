from datetime import datetime, timedelta, timezone

from app.core.rate_limiter import LoginRateLimiter


class TestLoginRateLimiter:
    def setup_method(self):
        self.limiter = LoginRateLimiter(max_attempts=5, window_seconds=60)

    def test_first_attempt_allowed(self):
        assert self.limiter.check('192.168.1.1', 'a@test.com') is True

    def test_five_attempts_allowed(self):
        ip = '192.168.1.1'
        email = 'a@test.com'
        for _ in range(5):
            self.limiter.record(ip, email)
        assert self.limiter.check(ip, email) is False

    def test_sixth_attempt_blocked(self):
        ip = '192.168.1.1'
        email = 'a@test.com'
        for _ in range(5):
            assert self.limiter.check(ip, email) is True
            self.limiter.record(ip, email)
        assert self.limiter.check(ip, email) is False

    def test_window_resets_after_one_minute(self):
        ip = '192.168.1.1'
        email = 'a@test.com'
        for _ in range(5):
            self.limiter.record(ip, email)

        old_attempts = self.limiter._attempts[f'{ip}:{email}']
        old_attempts[:] = [
            datetime.now(timezone.utc) - timedelta(seconds=90)
        ] * 5

        assert self.limiter.check(ip, email) is True

    def test_different_ips_do_not_share_limit(self):
        email = 'a@test.com'
        for _ in range(5):
            self.limiter.record('192.168.1.1', email)
        assert self.limiter.check('192.168.1.2', email) is True

    def test_different_emails_do_not_share_limit(self):
        ip = '192.168.1.1'
        for _ in range(5):
            self.limiter.record(ip, 'a@test.com')
        assert self.limiter.check(ip, 'b@test.com') is True

    def test_remaining_counts_down(self):
        ip = '192.168.1.1'
        email = 'a@test.com'
        assert self.limiter.remaining(ip, email) == 5
        self.limiter.record(ip, email)
        assert self.limiter.remaining(ip, email) == 4
        for _ in range(4):
            self.limiter.record(ip, email)
        assert self.limiter.remaining(ip, email) == 0
