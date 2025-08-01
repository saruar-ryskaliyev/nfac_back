from functools import lru_cache

from app.core.settings.app import AppSettings
from app.core.settings.base import AppEnvTypes, BaseAppSettings
from app.core.settings.dev import DevAppSettings
from app.core.settings.prod import ProdAppSettings
from app.core.settings.test import TestAppSettings
from typing import cast


environments = cast(
    dict[AppEnvTypes, type[AppSettings]],
    {
        AppEnvTypes.dev:  DevAppSettings,
        AppEnvTypes.prod: ProdAppSettings,
        AppEnvTypes.test: TestAppSettings,
    },
)


@lru_cache
def get_app_settings() -> AppSettings:
    base = BaseAppSettings()
    env_cls = environments[base.app_env]
    return env_cls(**base.model_dump())
