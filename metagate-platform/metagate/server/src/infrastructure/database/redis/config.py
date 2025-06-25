from typing import Optional, Annotated
from fastapi import Depends
from pydantic_settings import BaseSettings
import redis


class RedisConfig(BaseSettings):
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    database: int = 0

    class Config:
        env_prefix = "REDIS_"
        env_file = ".env.develop"
        extra = "ignore"

    @property
    def url(self) -> str:
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.database}"
        return f"redis://{self.host}:{self.port}/{self.database}"


class RedisEngine:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisEngine, cls).__new__(cls)
        return cls._instance

    def connect(self, config: RedisConfig = None):
        if self._client is None:
            if config is None:
                config = RedisConfig()

            self._client = redis.Redis(
                host=config.host,
                port=config.port,
                password=config.password,
                db=config.database,
                decode_responses=True
            )
            self._client.ping()

        return self._client

    def get_client(self):
        if self._client is None:
            self.connect()
        return self._client

    @property
    def client(self):
        if self._client is None:
            self.connect()
        return self._client


redis_engine = RedisEngine()


def get_redis():
    return redis_engine.get_client()


RedisDep = Annotated[redis.Redis, Depends(get_redis)]