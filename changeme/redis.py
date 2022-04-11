import aioredis
from sanic import Request, Sanic

from changeme.types.config import Settings


async def inject_session_req(request: Request):
    current_app = request.app
    pool = current_app.ctx.redis_pool
    redis = aioredis.Redis(connection_pool=pool, decode_responses=True)
    request.ctx.redis = redis


async def listener_redis(app: Sanic):
    pool = aioredis.ConnectionPool.from_url(
        app.config.REDIS_WEB, max_connections=app.config.REDIS_WEB_POOL_SIZE, decode_responses=True)
    app.ctx.redis_pool = pool


def sanic_init_redis(app: Sanic, settings: Settings):
    """
    A close middleware is not included because hte use of the pool:
    https://aioredis.readthedocs.io/en/latest/api/high-level/#aioredis.client.StrictRedis.close
    It will manager when to close connections. 
    """
    app.config.REDIS_WEB = settings.REDIS_WEB
    app.config.REDIS_WEB_POOL_SIZE = settings.REDIS_WEB_POOL_SIZE

    app.register_listener(listener_redis, "before_server_start")
    app.register_middleware(inject_session_req, "request")
