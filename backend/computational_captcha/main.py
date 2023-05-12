from typing import TYPE_CHECKING, cast

from computational_captcha.controllers import routes
from computational_captcha.env import SETTINGS
from litestar import Litestar
from litestar.config.response_cache import ResponseCacheConfig
from litestar.openapi import OpenAPIConfig
from litestar.stores.redis import RedisStore
from motor import motor_asyncio
from redis.asyncio import Redis

if TYPE_CHECKING:
    from computational_captcha.types import State


cache_store = RedisStore(
    redis=Redis(
        host=SETTINGS.redis.host, port=SETTINGS.redis.port, db=SETTINGS.redis.db
    )
)


async def init_mongo(state: "State") -> motor_asyncio.AsyncIOMotorCollection:
    if not getattr("state", "mongo", None):
        mongo = motor_asyncio.AsyncIOMotorClient(
            SETTINGS.mongo.host, SETTINGS.mongo.port
        )
        await mongo.server_info(None)
        state.mongo = cast(
            motor_asyncio.AsyncIOMotorCollection, mongo[SETTINGS.mongo.collection]
        )

    return state.mongo


async def init_redis(state: "State") -> RedisStore:
    if not getattr("state", "redis", None):
        state.redis = cache_store

    return state.redis


async def wipe_cache_on_shutdown() -> None:
    await cache_store.delete_all()


app = Litestar(
    route_handlers=[routes],
    on_startup=[init_mongo, init_redis],
    response_cache_config=ResponseCacheConfig(store=cache_store),
    before_shutdown=[wipe_cache_on_shutdown],
    openapi_config=OpenAPIConfig(
        title=SETTINGS.open_api.title, version=SETTINGS.open_api.version
    ),
)
