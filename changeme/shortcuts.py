from sanic import HTTPResponse, Sanic
from sanic.request import Request

from changeme.html_render import Render

_HTML_CONTENT = "text/html"


async def async_render(request: Request, tpl_name, data) -> HTTPResponse:
    render: Render = request.app.ctx.render
    tpl = await render.async_render(request, tpl_name, data=data)
    return HTTPResponse(tpl, content_type=_HTML_CONTENT)
