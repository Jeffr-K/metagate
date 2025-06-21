import logging
import sys

from structlog import configure
from structlog import get_logger as structlog_get_logger
from structlog.processors import JSONRenderer, TimeStamper, add_log_level
from structlog.stdlib import LoggerFactory

from .config import logger_config


def setup_logger():
    """로거 설정"""
    # 로그 레벨 설정
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, logger_config.level.upper()),
    )

    # Structlog 설정
    processors = [
        add_log_level,
        TimeStamper(fmt="iso"),
    ]

    if logger_config.format == "json":
        processors.append(JSONRenderer())

    configure(
        processors=processors,
        context_class=dict,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__):
    """structlog의 get_logger를 반환"""
    return structlog_get_logger(name)


# 로거 초기화
setup_logger()
logger = get_logger("metagate")
