from pydantic_settings import BaseSettings


class SentryConfig(BaseSettings):
    """Sentry 설정"""

    enabled: bool = False
    dsn: str | None = None
    environment: str = "development"
    traces_sample_rate: float = 1.0
    profiles_sample_rate: float = 1.0

    class Config:
        env_prefix = "SENTRY_"


# 전역 설정 인스턴스
sentry_config = SentryConfig()
