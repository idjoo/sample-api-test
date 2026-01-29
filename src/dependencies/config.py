from enum import StrEnum, auto
from os import environ
from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
    YamlConfigSettingsSource,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
        nested_model_default_partial_update=True,
        json_file=environ.get("CONFIG_JSON", "config.json"),
        toml_file=environ.get("CONFIG_TOML", "config.toml"),
        yaml_file=environ.get("CONFIG_YAML", "config.yaml"),
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls),
            JsonConfigSettingsSource(settings_cls),
            TomlConfigSettingsSource(settings_cls),
            init_settings,
        )


class Environment(StrEnum):
    LOCAL = auto()
    DEV = auto()
    PRD = auto()


class LoggingLevel(StrEnum):
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


class Logging(BaseModel):
    level: LoggingLevel = LoggingLevel.INFO


class Database(BaseModel):
    url: str | None = None
    kind: str = "postgresql"
    adapter: str = "psycopg"
    username: str = "username"
    password: str = "password"
    host: str = "localhost"
    port: int = 5432
    name: str = "database"


class BaseConfig(Settings):
    service: str = "oracle-sample-api"
    host: str = "0.0.0.0"
    port: int = 8080
    environment: Environment = Environment.LOCAL
    logging: Logging = Logging()
    database: Database = Database()


async def aget_config() -> BaseConfig:
    return BaseConfig()


def get_config() -> BaseConfig:
    return BaseConfig()


Config = Annotated[BaseConfig, Depends(aget_config)]
