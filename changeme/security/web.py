from functools import wraps
from inspect import isawaitable
from typing import Callable, List, Optional

from changeme import defaults
from changeme.errors.security import (AuthValidationFailed,
                                      MissingAuthorizationHeader,
                                      WebAuthFailed)
from changeme.managers import users_mg
from changeme.types.config import Settings
from changeme.types.security import JWTConfig, JWTResponse, UserLogin
from pydantic.error_wrappers import ValidationError
from sanic import Request, Sanic, json
from changeme.utils import get_from_module

from .base import AuthSpec


def get_auth(app_name=defaults.SANIC_APP_NAME) -> AuthSpec:
    """ a shortcut to get the Auth object from a web context """
    current_app: Sanic = Sanic.get_app(app_name)

    return current_app.ctx.auth


async def authenticate(request: Request, *args, **kwargs):
    try:
        creds = UserLogin(**request.json)
    except ValidationError as e:
        raise AuthValidationFailed()

    session = request.ctx.session
    async with session.begin():
        user = await users_mg.get_user_async(session, creds.username)
        if user is None:
            raise AuthValidationFailed()

        is_valid = users_mg.verify_password(
            user, creds.password, salt=request.app.config.AUTH_SALT)
        if not is_valid:
            raise AuthValidationFailed()

        return user


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


def sanic_init_auth(app: Sanic, auth: AuthSpec,  settings: Settings):
    app.ctx.auth = auth
    app.config.AUTH_SALT = settings.AUTH_SALT
    app.config.AUTH_ALLOW_REFRESH = settings.AUTH_ALLOW_REFRESH
    app.ctx.authenticate = get_from_module(settings.AUTH_FUNCTION)
