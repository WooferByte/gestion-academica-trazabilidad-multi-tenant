from pydantic import ConfigDict, Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='forbid',
    )

    database_url: PostgresDsn
    secret_key: str = Field(min_length=32)
    encryption_key: str = Field(min_length=32, max_length=32)
    access_token_expire_minutes: int = Field(default=15, ge=1)
    refresh_token_expire_days: int = Field(default=30, ge=1)
    debug: bool = Field(default=False, alias='DEBUG')
