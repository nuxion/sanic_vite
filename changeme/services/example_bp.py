from sanic import Blueprint
from sanic.response import empty, json, stream
from sanic_ext import openapi
from changeme.security.web import protected

example_bp = Blueprint("example_api", url_prefix="example", version="v1")


@example_bp.get("/<name>")
@openapi.parameter("name", str, "path")
@openapi.response(200, "Found")
@openapi.response(404, dict(msg=str), "Not Found")
@protected()
async def example_handler(request, name):
    return json(dict(msg=name), 200)
