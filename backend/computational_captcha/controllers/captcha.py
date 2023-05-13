import hashlib
import secrets
from base64 import b64encode
from typing import TYPE_CHECKING

from argon2 import low_level
from computational_captcha.env import SETTINGS
from computational_captcha.errors import (
    CaptchaComputedInvalidError,
    CaptchaNotFoundError,
)
from computational_captcha.models.captcha import CaptchaModel, GoalModel, ValidateModel
from litestar import Response, Router, post
from litestar.exceptions import NotAuthorizedException

if TYPE_CHECKING:
    from computational_captcha.types import State


@post(path="/generate", security=[{}], tags=["public"])
async def generate(
    state: "State",
) -> CaptchaModel:
    captcha_salt = secrets.token_bytes(16)

    time_cost = SETTINGS.captcha.argon.time_cost
    memory_cost = SETTINGS.captcha.argon.memory_cost
    parallelism = SETTINGS.captcha.argon.parallelism

    captcha_secrets = [
        secrets.token_urlsafe() for _ in range(SETTINGS.captcha.provided_secrets)
    ]

    selected_secrets = [
        captcha_secrets[index] for index in range(SETTINGS.captcha.required_secrets)
    ]
    argon_hashes = []
    goals = []

    for index, captcha_secret in enumerate(selected_secrets):
        encoded_secret = captcha_secret.encode(encoding="ascii")
        captcha_hash = low_level.hash_secret(
            secret=encoded_secret
            if len(argon_hashes) == 0
            else argon_hashes[index - 1] + encoded_secret,
            salt=captcha_salt,
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
            hash_len=32,
            type=low_level.Type.ID,
        )

        goals.append(
            GoalModel(sha256=hashlib.sha256(captcha_hash).hexdigest(), order=index)
        )
        argon_hashes.append(captcha_hash)

        await state.redis.set(
            captcha_secret, captcha_hash, SETTINGS.captcha.expire_seconds
        )

    # Shuffle list order after selecting secrets.
    secrets.SystemRandom().shuffle(captcha_secrets)

    return CaptchaModel(
        secrets=captcha_secrets,
        goals=goals,
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
    for goal in data.completed_goals:
        correct_argon2 = await state.redis.get(goal.secret)
        await state.redis.delete(goal.secret)

        if correct_argon2 != goal.argon2:
            raise CaptchaComputedInvalidError()

    return Response(None, status_code=200)


router = Router(path="/captcha", route_handlers=[validate, generate])
