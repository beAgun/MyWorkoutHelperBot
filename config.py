from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, Literal
from pydantic import PostgresDsn
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    DotEnvSettingsSource,
)
from zoneinfo import ZoneInfo
from datetime import tzinfo


class MyCustomSource:

    def __init__(self, dotenv_settings: DotEnvSettingsSource):
        self.dotenv_settings = dotenv_settings

    def __call__(self) -> dict[str, Any]:
        data = self.dotenv_settings()
        for prefix in ("", "TEST_"):
            data[f"{prefix}DATABASE_URL"] = str(
                PostgresDsn.build(
                    scheme="postgresql+asyncpg",
                    username=data[f"{prefix}DB_USER"],
                    password=data[f"{prefix}DB_PASS"],
                    host=data[f"{prefix}DB_HOST"],
                    port=int(data[f"{prefix}DB_PORT"]),
                    path=data[f"{prefix}DB_NAME"],
                )
            )
        return data


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    BOT_TOKEN: str
    WEBHOOK_URL: str
    WEBHOOK_PATH: str

    MODE: Literal["DEV", "TEST", "PROD"]
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    CONSOLE_LOG: bool
    FILE_LOG: bool
    FILE_LOG_FILENAME: str

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DATABASE_URL: str

    TEST_DB_HOST: str
    TEST_DB_PORT: int
    TEST_DB_USER: str
    TEST_DB_PASS: str
    TEST_DB_NAME: str
    TEST_DATABASE_URL: str

    LOCAL_TZ: tzinfo = ZoneInfo("Europe/Moscow")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ):
        return env_settings, MyCustomSource(dotenv_settings)


settings = Settings()
