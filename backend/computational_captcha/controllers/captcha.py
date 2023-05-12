import secrets
from base64 import b64encode
from typing import TYPE_CHECKING

from argon2.low_level import hash_secret
from argon2.profiles import RFC_9106_LOW_MEMORY
from bson import ObjectId
from computational_captcha.errors import (
    CaptchaComputedInvalidError,
    CaptchaNotFoundError,
)
from computational_captcha.models.captcha import CaptchaModel, ValidateModel
from litestar import Response, Router, post

if TYPE_CHECKING:
    from computational_captcha.types import State


@post(path="/generate")
async def generate(state: "State") -> CaptchaModel:
    captcha_secret = secrets.token_bytes(32)
    captcha_salt = secrets.token_bytes(RFC_9106_LOW_MEMORY.salt_len)

    captcha_hash = hash_secret(
        secret=captcha_secret,
        salt=captcha_salt,
        time_cost=RFC_9106_LOW_MEMORY.time_cost,
        memory_cost=RFC_9106_LOW_MEMORY.memory_cost,
        parallelism=RFC_9106_LOW_MEMORY.parallelism,
        hash_len=RFC_9106_LOW_MEMORY.hash_len,
        type=RFC_9106_LOW_MEMORY.type,
    )

    result = await state.mongo.captcha.insert_one({"hash": captcha_hash.decode()})

    return CaptchaModel(
        _id=str(result.inserted_id),
        secret=b64encode(captcha_secret).decode(),
        salt=b64encode(captcha_salt).decode(),
    )


@post(path="/validate", status_code=200, raises=[CaptchaNotFoundError])
async def validate(data: ValidateModel, state: "State") -> Response:
    search = {"_id": ObjectId(data.id)}
    result = await state.mongo.captcha.find_one(search)
    if not result:
        raise CaptchaNotFoundError()

    await state.mongo.captcha.delete_one(search)

    if result["hash"] != data.computed_hash:
        raise CaptchaComputedInvalidError()

    return Response(None, status_code=200)


router = Router(path="/captcha", route_handlers=[validate, generate])
