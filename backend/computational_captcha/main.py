from typing import TYPE_CHECKING, cast

from computational_captcha.bearer_auth import BearerAuthentication
from computational_captcha.controllers import routes
from computational_captcha.env import SETTINGS
from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.middleware.base import DefineMiddleware
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.openapi import OpenAPIConfig
from litestar.stores.redis import RedisStore
from redis.asyncio import Redis

if TYPE_CHECKING:
    from computational_captcha.types import State

rate_limit_config = RateLimitConfig(
    rate_limit=SETTINGS.captcha.rate_limit, exclude=["/schema"]
)

cache_store = RedisStore(
    redis=Redis(
        host=SETTINGS.redis.host, port=SETTINGS.redis.port, db=SETTINGS.redis.db
    )
)


async def init_redis(state: "State") -> RedisStore:
    if not getattr("state", "redis", None):
        state.redis = cache_store

    return state.redis


async def wipe_cache_on_shutdown() -> None:
    await cache_store.delete_all()


app = Litestar(
    route_handlers=[routes],
    on_startup=[init_redis],
    before_shutdown=[wipe_cache_on_shutdown],
    middleware=[
        rate_limit_config.middleware,
        DefineMiddleware(
            BearerAuthentication, exclude=["/schema", "/controller/captcha/generate"]
        ),
    ],
    openapi_config=OpenAPIConfig(
        title=SETTINGS.open_api.title, version=SETTINGS.open_api.version
    ),
    cors_config=CORSConfig(
        allow_origins=SETTINGS.captcha.allowed_hosts,
        allow_methods=["POST"],
        allow_credentials=False,
    ),
)
