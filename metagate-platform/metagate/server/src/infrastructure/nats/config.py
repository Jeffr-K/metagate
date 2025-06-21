from pydantic_settings import BaseSettings


class NatsConfig(BaseSettings):
    """NATS 설정"""

    enabled: bool = False
    servers: list[str] = ["nats://localhost:4222"]
    client_name: str = "metagate-server"
    reconnect_time_wait: int = 2
    max_reconnect_attempts: int = 60
    ping_interval: int = 20
    max_outstanding_pings: int = 5

    # 인증 설정
    username: str | None = None
    password: str | None = None
    token: str | None = None

    class Config:
        env_prefix = "NATS_"


# 전역 설정 인스턴스
nats_config = NatsConfig()
