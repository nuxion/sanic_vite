import json as std_json
from importlib import import_module
from typing import List, Optional

from sanic import Sanic
from sanic.response import json
from sanic_ext import Extend

from changeme import defaults
from changeme.html_render import Render
from changeme.html_render.vite import ViteDev
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


def app_init(
        settings: Settings,
        services_bp: Optional[List[str]] = None,
        pages_bp: Optional[List[str]] = None

):

    _app = Sanic(settings.SANIC_APP_NAME)

    _app.config.CORS_ORIGINS = settings.CORS_ORIGINS
    _app.config.CORS_ALLOW_HEADERS = settings.CORS_ALLOW_HEADERS

    render: Render = Render(searchpath=settings.TEMPLATES_DIR)

    manifest_json = open_json((f"{settings.BASE_PATH}/{settings.VITE_OUTPUT_DIR}/"
                               "manifest.json"))

    render.init_app(_app)
    render.add_extension(ViteDev)
    render.env.vite_dev_server = f"{settings.VITE_DEV_SERVER}/{settings.VITE_BASE}"
    render.env.vite_dev_mode = settings.VITE_DEV_MODE
    render.env.vite_static_url = settings.VITE_STATIC_URL_PATH
    render.env.vite_manifest = manifest_json

    # Extend(_app)
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
    # _app.ext.openapi.secured()
    _app.ext.openapi.secured("token")

    # _app.static(settings.STATIC_URL_PATH, settings.STATIC_LOCAL_DIR)
    if settings.VITE_DEV_MODE:
        static_dir = f"{settings.BASE_PATH}/{settings.VITE_STATIC_DIR}"
        _app.static(settings.VITE_STATIC_URL_PATH, static_dir)

    for k, v in settings.STATICFILES_DIRS.items():
        _app.static(k, v)

    @_app.get("/status")
    async def status_handler(request):
        return json(dict(msg="We are ok", version=version))

    @_app.get("/")
    async def index_handler(request):
        return json(dict(msg="We are ok"))

    return _app


# app = app_init()
