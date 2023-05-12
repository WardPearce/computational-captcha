from pydantic import AnyHttpUrl, BaseModel, BaseSettings


class MongoDB(BaseModel):
    host: str = "localhost"
    port: int = 27017
    collection: str = "canary"


class ProxiedUrls(BaseModel):
    frontend: AnyHttpUrl = AnyHttpUrl(url="localhost", scheme="http")
    backend: AnyHttpUrl = AnyHttpUrl(url="localhost/api", scheme="http")


class OpenAPI(BaseModel):
    title: str = "computational-captcha"
    version: str = "0.0.1"


class Redis(BaseModel):
    host: str = "redis://localhost/"
    port: int = 6379
    db: int = 0


class Settings(BaseSettings):
    mongo: MongoDB = MongoDB()
    redis: Redis = Redis()
    proxy_urls: ProxiedUrls = ProxiedUrls()
    open_api: OpenAPI = OpenAPI()

    class Config:
        env_prefix = "cc_"


SETTINGS = Settings()  # type: ignore
