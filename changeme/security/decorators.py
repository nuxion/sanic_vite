from functools import wraps
from inspect import isawaitable
from typing import Optional, Tuple

from changeme import defaults
from changeme.types.security import JWTConfig
from sanic import Request, Sanic, json

from .authentication import Auth


def _get_token(request: Request, header_name: str) -> Optional[Tuple[Optional[str], str]]:
    """Attempt to return the auth header token.
    :return: If header exists, optional token prefix and token.
    """
    auth_header = request.headers.getone(header_name, None)

    if auth_header is not None:
        auth_header = auth_header.split(" ", 1)

        if len(auth_header) == 1:
            auth_header = (None, auth_header[0])

    return auth_header


def init_auth(app: Sanic, conf: JWTConfig):
    auth = Auth(conf)

    app.ctx.auth = auth


def get_auth() -> Auth:
    current_app: Sanic = Sanic.get_app(defaults.SANIC_APP_NAME)

    return current_app.ctx.auth


def protected(scopes=None):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):

            auth = get_auth()
            auth_header = _get_token(request, auth.conf.header_name)
            try:
                decoded = auth.decode(auth_header)
                request.ctx.decoded = decoded
                response = f(request, *args, **kwargs)
                if isawaitable(response):
                    response = await response
            except Exception:
                response = json({"status": "not authorized"}, 403)

            return response

        return decorated_function

    return decorator
