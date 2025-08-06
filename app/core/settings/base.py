from enum import Enum
from typing import cast
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvTypes(str, Enum):
    prod = "prod"
    dev = "dev"
    test = "test"


class BaseAppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_env: AppEnvTypes = AppEnvTypes.dev
    gemini_api_key: SecretStr
