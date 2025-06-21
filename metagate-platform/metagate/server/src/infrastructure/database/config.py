from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    """데이터베이스 설정"""

    host: str = "localhost"
    port: int = 5432
    username: str = "postgres"
    password: str = "password"
    database: str = "metagate"

    @property
    def url(self) -> str:
        """PostgreSQL 연결 URL"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

    class Config:
        env_prefix = "DB_"


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
db_config = DatabaseConfig()
redis_config = RedisConfig()
