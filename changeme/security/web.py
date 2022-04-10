from functools import wraps
from inspect import isawaitable
from typing import List, Optional

from changeme import defaults
from changeme.errors.security import (AuthValidationFailed,
                                      MissingAuthorizationHeader,
                                      WebAuthFailed)
from changeme.types.config import Settings
from changeme.types.security import JWTConfig
from sanic import Request, Sanic, json

from .authentication import Auth


def get_auth(app_name=defaults.SANIC_APP_NAME) -> Auth:
    """ a shortcut to get the Auth object from a web context """
    current_app: Sanic = Sanic.get_app(app_name)

    return current_app.ctx.auth


def protected(scopes: Optional[List[str]] = None,
              require_all=True):
    """ verify a token from a request.
    Optionally if a list of scopes is given then will check that scopes
    with the scopes provided by the token.

    :param scopes: a list of scopes
    :param required_all: if true it will check that the all the names provided
    match with the required.

    """

    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            auth = get_auth()
            token = request.token
            if not token:
                raise MissingAuthorizationHeader()
            try:
                decoded = auth.validate(token, scopes, require_all)
                request.ctx.token_data = decoded
                response = f(request, *args, **kwargs)
                if isawaitable(response):
                    response = await response
            except AuthValidationFailed:
                raise WebAuthFailed()

            return response

        return decorated_function

    return decorator
