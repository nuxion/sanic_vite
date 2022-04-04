from changeme.shortcuts import async_render
from changeme.types.html import HtmlData
from sanic import Blueprint
from sanic.response import empty, json, stream

example_bp = Blueprint("example", url_prefix="example")


def new_data(content):
    return HtmlData(
        ctx={"DEV": True},
        title="changeme - site",
        content=content
    )


@example_bp.get("/")
async def example_template(request):
    data = new_data(dict(msg="hello"))
    return await async_render(request, "example/index.html", data)
