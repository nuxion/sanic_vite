from changeme.security import get_auth, protected
from changeme.types.security import JWTResponse, UserLogin
from sanic import Blueprint
from sanic.response import empty, json, stream
from sanic_ext import openapi

users_mock = {"nuxion": "test"}

auth_bp = Blueprint("auth_api", url_prefix="auth", version="v1")


@auth_bp.post("/_login")
@openapi.response(200, {"application/json": JWTResponse})
@openapi.response(403, dict(msg=str), "Not Found")
@openapi.body(UserLogin)
async def login_handler(request):
    creds = UserLogin(**request.json)
    if users_mock.get(creds.username):
        auth = get_auth()
        encoded = auth.encode({"usr": creds.username})
        return json(JWTResponse(access_token=encoded).dict(), 200)
    return json(dict(msg="error"), 403)


@auth_bp.get("/_verify")
@openapi.response(200, {"application/json": JWTResponse})
@protected()
async def verify_handler(request):
    return json(request.ctx.token_data, 200)
