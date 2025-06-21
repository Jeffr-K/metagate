from pydantic_settings import BaseSettings


class PrometheusConfig(BaseSettings):
    """Prometheus 설정"""

    enabled: bool = True
    port: int = 9090
    host: str = "0.0.0.0"

    # 메트릭 설정
    request_duration_buckets: list = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
    request_size_buckets: list = [100, 1000, 10000, 100000, 1000000]

    class Config:
        env_prefix = "PROMETHEUS_"


# 전역 설정 인스턴스
prometheus_config = PrometheusConfig()
