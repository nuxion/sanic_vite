import json as std_json
from importlib import import_module
from typing import List, Optional

from sanic import Sanic
from sanic.response import json
from sanic_ext import Extend

from changeme import defaults
from changeme.html_render import Render
from changeme.html_render.static import Static
from changeme.html_render.vite import ViteAsset, ViteDev
from changeme.security import Auth
from changeme.types.config import Settings
from changeme.utils import get_version, open_json, path_norm

version = get_version("__version__.py")


def init_blueprints(app, blueprints_allowed, package_dir):
    """
    It will import bluprints from modules that ends with "_bp" and belongs
    to the package declared in `changeme.defaults.SANIC_BLUPRINTS_DIR`
    by default it will be `changeme.services`
    """
    blueprints = set()
    mod = app.__module__
    for mod_name in blueprints_allowed:
        modules = import_module(
            f"{package_dir}.{mod_name}_bp", mod)
        for el in dir(modules):
            if el.endswith("_bp"):
                bp = getattr(modules, el)
                blueprints.add(bp)

    for bp in blueprints:
        print("Adding blueprint: ", bp.name)
        app.blueprint(bp)


def create_app(
        settings: Settings,
        services_bp: Optional[List[str]] = None,
        pages_bp: Optional[List[str]] = None,
        with_render=True,
        with_vite=False,
        auth_bp=True,
) -> Sanic:

    _app = Sanic(settings.SANIC_APP_NAME)

    _app.config.CORS_ORIGINS = settings.CORS_ORIGINS
    _app.config.CORS_ALLOW_HEADERS = settings.CORS_ALLOW_HEADERS

    if with_render:
        render: Render = Render(searchpath=settings.TEMPLATES_DIR)
        render.init_app(_app)
        if with_vite:
            render.add_vite(_app, settings)

    # Extend(_app)
    auth = Auth.from_settings(settings)
    auth.init_app(_app)

    _app.ext.openapi.add_security_scheme(
        "token",
        "http",
        scheme="bearer",
        bearer_format="JWT",
    )

    if services_bp:
        init_blueprints(_app, services_bp, defaults.SANIC_SERVICES_DIR)
    if pages_bp:
        init_blueprints(_app, services_bp, defaults.SANIC_PAGES_DIR)
    if auth_bp:
        init_blueprints(_app, ["auth"], "changeme.security")
    # _app.ext.openapi.secured()
    _app.ext.openapi.secured("token")

    for _, v in settings.STATICFILES_DIRS.items():
        _app.static(v["uripath"], v["localdir"])

    @_app.get("/status")
    async def status_handler(request):
        return json(dict(msg="We are ok", version=version))

    @_app.get("/")
    async def index_handler(request):
        return json(dict(msg="We are ok"))

    return _app


# app = app_init()
