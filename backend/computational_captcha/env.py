from typing import List, Tuple

from argon2.profiles import RFC_9106_LOW_MEMORY
from litestar.middleware.rate_limit import DurationUnit
from pydantic import BaseModel, BaseSettings, Field


class Redis(BaseModel):
    host: str = "localhost"
    port: int = 6379
    db: int = 1


class OpenAPI(BaseModel):
    title: str = "computational-captcha"
    version: str = "0.0.1"


class ArgonParameters(BaseModel):
    time_cost: int = RFC_9106_LOW_MEMORY.time_cost
    memory_cost: int = RFC_9106_LOW_MEMORY.memory_cost
    parallelism: int = RFC_9106_LOW_MEMORY.parallelism


class Captcha(BaseModel):
    allowed_hosts: List[str] = []
    rate_limit: Tuple[DurationUnit, int] = ("minute", 30)
    expire_seconds: int = 120
    api_key: str = Field(..., min_length=32)
    groups: List[str] = ["main"]
    argon: ArgonParameters = ArgonParameters()


class Settings(BaseSettings):
    redis: Redis = Redis()
    open_api: OpenAPI = OpenAPI()
    captcha: Captcha

    class Config:
        env_prefix = "cc_"


SETTINGS = Settings()  # type: ignore
