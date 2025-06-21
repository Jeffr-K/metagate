import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from .config import sentry_config


def init_sentry():
    """Sentry 초기화"""
    if not sentry_config.enabled or not sentry_config.dsn:
        return

    sentry_sdk.init(
        dsn=sentry_config.dsn,
        environment=sentry_config.environment,
        traces_sample_rate=sentry_config.traces_sample_rate,
        profiles_sample_rate=sentry_config.profiles_sample_rate,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
            RedisIntegration(),
        ],
        # 성능 모니터링 설정
        enable_tracing=True,
        # 에러 필터링
        before_send=lambda event, hint: event,
    )


def capture_exception(exception: Exception, **kwargs):
    """예외 캡처"""
    if sentry_config.enabled:
        sentry_sdk.capture_exception(exception, **kwargs)


def capture_message(message: str, level: str = "info", **kwargs):
    """메시지 캡처"""
    if sentry_config.enabled:
        sentry_sdk.capture_message(message, level=level, **kwargs)


def set_user(user_id: str, **kwargs):
    """사용자 정보 설정"""
    if sentry_config.enabled:
        sentry_sdk.set_user({"id": user_id, **kwargs})


def set_tag(key: str, value: str):
    """태그 설정"""
    if sentry_config.enabled:
        sentry_sdk.set_tag(key, value)


def set_context(name: str, data: dict):
    """컨텍스트 설정"""
    if sentry_config.enabled:
        sentry_sdk.set_context(name, data)
