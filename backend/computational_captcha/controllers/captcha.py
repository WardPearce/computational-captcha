import secrets
from base64 import b64encode
from typing import TYPE_CHECKING

from argon2 import low_level
from computational_captcha.env import SETTINGS
from computational_captcha.errors import (
    CaptchaComputedInvalidError,
    CaptchaNotFoundError,
)
from computational_captcha.models.captcha import CaptchaModel, ValidateModel
from litestar import Response, Router, post
from litestar.exceptions import NotAuthorizedException

if TYPE_CHECKING:
    from computational_captcha.types import State


@post(path="/generate", security=[{}], tags=["public"])
async def generate(
    state: "State",
) -> CaptchaModel:
    captcha_secret = secrets.token_bytes(32)
    captcha_salt = secrets.token_bytes(16)

    time_cost = SETTINGS.captcha.argon.time_cost
    memory_cost = SETTINGS.captcha.argon.memory_cost
    parallelism = SETTINGS.captcha.argon.parallelism

    captcha_hash = low_level.hash_secret(
        secret=captcha_secret,
        salt=captcha_salt,
        time_cost=time_cost,
        memory_cost=memory_cost,
        parallelism=parallelism,
        hash_len=32,
        type=low_level.Type.ID,
    )

    captcha_id = secrets.token_urlsafe(32)

    await state.redis.set(
        captcha_id, captcha_hash.decode(), SETTINGS.captcha.expire_seconds
    )

    return CaptchaModel(
        id=captcha_id,
        secret=b64encode(captcha_secret).decode(),
        salt=b64encode(captcha_salt).decode(),
        time_cost=time_cost,
        memory_cost=memory_cost,
        parallelism=parallelism,
    )


@post(
    path="/validate",
    status_code=200,
    raises=[CaptchaNotFoundError, CaptchaComputedInvalidError, NotAuthorizedException],
    tags=["internal"],
)
async def validate(data: ValidateModel, state: "State") -> Response:
    correct_hash = await state.redis.get(data.id)
    if not correct_hash:
        raise CaptchaNotFoundError()

    await state.redis.delete(data.id)

    if correct_hash != data.computed_hash:
        raise CaptchaComputedInvalidError()

    return Response(None, status_code=200)


router = Router(path="/captcha", route_handlers=[validate, generate])
