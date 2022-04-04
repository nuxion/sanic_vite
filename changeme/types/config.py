from typing import Dict, List, Optional, Union, Any

from changeme import defaults
from pydantic import BaseSettings


class Settings(BaseSettings):
    BASE_PATH: str
    LISTEN_ADDR: str = "localhost:8000"

    TEMPLATES_DIR: Optional[str] = None
    TEMPLATES_PACKAGE_NAME: Optional[str] = None
    DEV_MODE: bool = True

    STATIC_URL: str = ""
    STATICFILES_DIRS: Dict[str, str] = {"/": "public/"}

    VITE_STATIC_URL_PATH: str = "/static/assets"
    VITE_STATIC_DIR: str = "templates/static/src/assets"
    VITE_OUTPUT_DIR: str = "dist/vite"
    VITE_DEV_SERVER: str = "http://localhost:3000"
    VITE_DEV_MODE: bool = True
    VITE_BASE: str = "static"

    CORS_ORIGINS: Union[List, str] = "*"
    CORS_ALLOW_HEADERS: Union[List, str] = "*"
    SANIC_APP_NAME = defaults.SANIC_APP_NAME

    class Config:
        env_prefix = "CHANGEME_"