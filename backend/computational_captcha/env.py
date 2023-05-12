from typing import List, Tuple

from litestar.middleware.rate_limit import DurationUnit
from pydantic import BaseModel, BaseSettings, Field


class MongoDB(BaseModel):
    host: str = "localhost"
    port: int = 27017
    collection: str = "computational-captcha"


class OpenAPI(BaseModel):
    title: str = "computational-captcha"
    version: str = "0.0.1"


class Captcha(BaseModel):
    allowed_hosts: List[str] = []
    rate_limit: Tuple[DurationUnit, int] = ("minute", 30)
    expire_seconds: int = 120
    api_key: str = Field(..., min_length=32)


class Settings(BaseSettings):
    mongo: MongoDB = MongoDB()
    open_api: OpenAPI = OpenAPI()
    captcha: Captcha

    class Config:
        env_prefix = "cc_"


SETTINGS = Settings()  # type: ignore
