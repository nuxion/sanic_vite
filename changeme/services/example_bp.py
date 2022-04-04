from sanic import Blueprint
from sanic.response import empty, json, stream
from sanic_ext import openapi

example_bp = Blueprint("example_api", url_prefix="example", version="1")


@example_bp.get("/<name>")
@openapi.parameter("name", str, "path")
@openapi.response(200, "Found")
@openapi.response(404, dict(msg=str), "Not Found")
async def example_handler(request, name):
    return json(dict(msg=name), 200)
