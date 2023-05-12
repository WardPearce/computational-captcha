from litestar.datastructures.state import State as BaseState
from litestar.stores.redis import RedisStore


class State(BaseState):
    redis: RedisStore
