from changeme.errors.security import (AuthValidationFailed,
                                      MissingAuthorizationHeader,
                                      WebAuthFailed)
from changeme.security import get_auth, protected
from changeme.types.security import JWTResponse, UserLogin
from sanic import Blueprint, Request
from sanic.response import empty, json, stream
from sanic_ext import openapi

auth_bp = Blueprint("auth_api", url_prefix="auth", version="v1")


@auth_bp.post("/_login")
@openapi.response(200, {"application/json": JWTResponse})
@openapi.response(403, dict(msg=str), "Not Found")
@openapi.body(UserLogin)
async def login_handler(request):
    auth = get_auth()
    try:
        user = await auth.authenticate(request)
    except AuthValidationFailed:
        raise WebAuthFailed()
    encoded = auth.encode({"usr": user.username,
                           "scopes": user.scopes.split(",")})

    rtkn = await auth.store_refresh_token(request.ctx.redis, user.username)
    return json(JWTResponse(access_token=encoded, refresh_token=rtkn).dict(), 200)


@auth_bp.get("/_verify")
@openapi.response(200, {"application/json": JWTResponse})
@protected()
async def verify_handler(request):
    return json(request.ctx.token_data, 200)


@auth_bp.post("/_refresh_token")
@openapi.response(200, {"application/json": JWTResponse})
@openapi.body(JWTResponse)
async def refresh_handler(request):
    if not request.app.config.ALLOW_REFRESH:
        return json(dict(msg="Not found"), 404)

    old_token = JWTResponse(**request.json)
    redis = request.ctx.redis
    auth = get_auth()
    try:
        jwt_res = await auth.refresh_token(redis, old_token.access_token, old_token.refresh_token)
        return json(new_jwt.dict(), 200)
    except AuthValidationFailed():
        raise WebAuthFailed()
