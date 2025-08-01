from enum import Enum
from typing import cast
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvTypes(str, Enum):
    prod = "prod"
    dev = "dev"
    test = "test"


class BaseAppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_env: AppEnvTypes = AppEnvTypes.dev
