from pydantic_settings import BaseSettings


class RedisConfig(BaseSettings):
    """Redis 설정"""

    host: str = "localhost"
    port: int = 6379
    password: str | None = None
    database: int = 0

    @property
    def url(self) -> str:
        """Redis 연결 URL"""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.database}"
        return f"redis://{self.host}:{self.port}/{self.database}"

    class Config:
        env_prefix = "REDIS_"


# 전역 설정 인스턴스
redis_config = RedisConfig()
