from pathlib import PosixPath, WindowsPath
from typing import Any, Dict, List, Optional, Union

from changeme import defaults
from pydantic import BaseModel, BaseSettings, RedisDsn

from .security import JWTConfig


class Migration(BaseModel):
    models: List[str]
    migrations_module: str
    version_table: str 


class Settings(BaseSettings):
    BASE_PATH: Union[str, PosixPath, WindowsPath]
    LISTEN_ADDR: str = "localhost:8000"

    SQL: str = "sqlite:///sqlite.db"
    ASQL: str = "sqlite+aiosqlite:///sqlite.db"
    REDIS_WEB: RedisDsn = "redis://localhost:6379/0"
    REDIS_WEB_POOL_SIZE: int = 10
    TEMPLATES_DIR: Optional[str] = None
    TEMPLATES_PACKAGE_NAME: Optional[str] = None
    DEV_MODE: bool = False

    STATIC_URL: str = ""
    STATICFILES_DIRS: Dict[str, Any] = {
        "public": {"uripath": "", "localdir": "public/"},
    }

    VITE_STATIC_URL_PATH: str = "/static/assets"
    VITE_STATIC_DIR: str = "templates/static/src/assets"
    VITE_OUTPUT_DIR: str = "dist/vite"
    VITE_DEV_SERVER: str = "http://localhost:3000"
    VITE_DEV_MODE: bool = False
    VITE_REACT_MODE: bool = False
    VITE_BASE: str = "static"

    JWT_ALG: str = defaults.JWT_ALG
    JWT_EXP: int = 30
    JWT_PUBLIC: str = "secrets/ecdsa.pub.pem"
    JWT_PRIVATE: str = "secrets/ecdsa.priv.pem"
    JWT_REQUIRES_CLAIMS: List[str] = ["exp"]
    JWT_SECRET: Optional[str] = None
    JWT_ISS: Optional[str] = None
    JWT_AUD: Optional[str] = None
    AUTH_SALT: str = "changeit"
    AUTH_ALLOW_REFRESH: bool = True
    AUTH_CLASS = "changeme.security.authentication.Auth"
    AUTH_FUNCTION = "changeme.security.web.authenticate"
    MIGRATIONS: Dict[str, Migration] = {}

    CORS_ORIGINS: Union[List, str] = "*"
    CORS_ALLOW_HEADERS: Union[List, str] = "*"
    SANIC_APP_NAME = defaults.SANIC_APP_NAME
    SETTINGS_MODULE: Optional[str] = None

    class Config:
        env_prefix = "CHANGEME_"
