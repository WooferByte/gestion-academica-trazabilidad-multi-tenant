import os

import pytest


class TestSettingsValid:
    def test_instantiates_with_valid_env(self):
        os.environ['DATABASE_URL'] = 'postgresql+asyncpg://u:p@localhost:5432/db'
        os.environ['SECRET_KEY'] = 'a-secret-key-that-is-at-least-32-characters!'
        os.environ['ENCRYPTION_KEY'] = 'encr-key-exactly-32-chars-long!!'

        from app.core.config import Settings

        settings = Settings()  # type: ignore
        assert str(settings.database_url) == 'postgresql+asyncpg://u:p@localhost:5432/db'
        assert settings.secret_key == 'a-secret-key-that-is-at-least-32-characters!'
        assert settings.encryption_key == 'encr-key-exactly-32-chars-long!!'
        assert settings.access_token_expire_minutes == 15

    def test_default_access_token_expire_minutes(self):
        os.environ['DATABASE_URL'] = 'postgresql+asyncpg://u:p@localhost:5432/db'
        os.environ['SECRET_KEY'] = 'b-secret-key-that-is-at-least-32-characters!'
        os.environ['ENCRYPTION_KEY'] = 'encr-key-exactly-32-chars-long!!'

        from app.core.config import Settings

        settings = Settings()  # type: ignore
        assert settings.access_token_expire_minutes == 15


class TestSettingsMissingRequired:
    def test_fails_when_database_url_missing(self):
        os.environ.pop('DATABASE_URL', None)
        os.environ['SECRET_KEY'] = 'c-secret-key-that-is-at-least-32-characters!'
        os.environ['ENCRYPTION_KEY'] = 'encr-key-exactly-32-chars-long!!'

        from app.core.config import Settings

        with pytest.raises(Exception):
            Settings()  # type: ignore

    def test_fails_when_secret_key_too_short(self):
        os.environ['DATABASE_URL'] = 'postgresql+asyncpg://u:p@localhost:5432/db'
        os.environ['SECRET_KEY'] = 'short'
        os.environ['ENCRYPTION_KEY'] = 'encr-key-exactly-32-chars-long!!'

        from app.core.config import Settings

        with pytest.raises(Exception):
            Settings()  # type: ignore

    def test_fails_when_encryption_key_wrong_length(self):
        os.environ['DATABASE_URL'] = 'postgresql+asyncpg://u:p@localhost:5432/db'
        os.environ['SECRET_KEY'] = 'd-secret-key-that-is-at-least-32-characters!'
        os.environ['ENCRYPTION_KEY'] = 'too-short'

        from app.core.config import Settings

        with pytest.raises(Exception):
            Settings()  # type: ignore

    def test_fails_when_invalid_url_type(self):
        os.environ['DATABASE_URL'] = 'not-a-valid-url'
        os.environ['SECRET_KEY'] = 'e-secret-key-that-is-at-least-32-characters!'
        os.environ['ENCRYPTION_KEY'] = 'encr-key-exactly-32-chars-long!!'

        from app.core.config import Settings

        with pytest.raises(Exception):
            Settings()  # type: ignore
