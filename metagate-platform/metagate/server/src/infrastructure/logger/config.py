from pydantic_settings import BaseSettings


class LoggerConfig(BaseSettings):
    """로거 설정"""

    level: str = "INFO"
    format: str = "json"  # json, text
    output: str = "stdout"  # stdout, file

    # 파일 로깅 설정
    log_file: str | None = None
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

    class Config:
        env_prefix = "LOG_"


# 전역 설정 인스턴스
logger_config = LoggerConfig()
