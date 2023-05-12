from typing import TYPE_CHECKING, cast

from computational_captcha.bearer_auth import BearerAuthentication
from computational_captcha.controllers import routes
from computational_captcha.env import SETTINGS
from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.middleware.base import DefineMiddleware
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.openapi import OpenAPIConfig
from motor import motor_asyncio

if TYPE_CHECKING:
    from computational_captcha.types import State


rate_limit_config = RateLimitConfig(
    rate_limit=SETTINGS.captcha.rate_limit, exclude=["/schema"]
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


app = Litestar(
    route_handlers=[routes],
    on_startup=[init_mongo],
    middleware=[
        rate_limit_config.middleware,
        DefineMiddleware(BearerAuthentication, exclude="schema"),
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
