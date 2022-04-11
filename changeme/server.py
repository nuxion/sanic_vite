import json as std_json
from importlib import import_module
from typing import Callable, List, Optional

from sanic import Sanic
from sanic.response import json
from sanic_ext import Extend

from changeme import defaults
from changeme.html_render import Render
from changeme.html_render.static import Static
from changeme.html_render.vite import ViteAsset, ViteDev
from changeme.security import AuthSpec, sanic_init_auth
from changeme.types.config import Settings
from changeme.utils import get_from_module, get_version, open_json, path_norm

version = get_version("__version__.py")


async def status_handler(request):
    return json(dict(msg="We are ok", version=version))


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


def init_db(app: Sanic, settings: Settings):
    from changeme.db.web import sanic_init_db
    sanic_init_db(app, settings)


def init_redis(app: Sanic, settings: Settings):
    from changeme.redis import sanic_init_redis
    sanic_init_redis(app, settings)


def create_app(
        settings: Settings,
        services_bp: Optional[List[str]] = None,
        pages_bp: Optional[List[str]] = None,
        with_render=True,
        with_vite=False,
        with_db=True,
        with_redis=True,
        with_auth=True,
        with_auth_bp=True,
) -> Sanic:
    """ Factory pattern for the creation of a Sanic Web app """

    _app = Sanic(settings.SANIC_APP_NAME)

    _app.config.CORS_ORIGINS = settings.CORS_ORIGINS
    _app.config.CORS_ALLOW_HEADERS = settings.CORS_ALLOW_HEADERS

    if with_render:
        render: Render = Render(searchpath=settings.TEMPLATES_DIR)
        render.init_app(_app)
        if with_vite:
            render.add_vite(_app, settings)

    if with_db:
        init_db(_app, settings=settings)

    if with_redis:
        init_redis(_app, settings=settings)

    if with_auth:
        AuthClass = get_from_module(settings.AUTH_CLASS)
        auth: AuthSpec = AuthClass.from_settings(settings)
        sanic_init_auth(_app, auth, settings)
    if with_auth and with_auth_bp:
        init_blueprints(_app, ["auth"], "changeme.security")

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

    for _, v in settings.STATICFILES_DIRS.items():
        _app.static(v["uripath"], v["localdir"])

    _app.add_route(status_handler, "/status")
    return _app
