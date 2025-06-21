import json
from typing import Any

import redis

from .config import redis_config


class RedisClient:
    """Redis 클라이언트 래퍼"""

    def __init__(self):
        self.client = redis.Redis(
            host=redis_config.host,
            port=redis_config.port,
            password=redis_config.password,
            db=redis_config.database,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )

    def set(self, key: str, value: Any, expire: int | None = None) -> bool:
        """값 설정"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return self.client.set(key, value, ex=expire)

    def get(self, key: str) -> Any | None:
        """값 조회"""
        value = self.client.get(key)
        if value is None:
            return None

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    def delete(self, key: str) -> int:
        """키 삭제"""
        return self.client.delete(key)

    def exists(self, key: str) -> bool:
        """키 존재 여부 확인"""
        return bool(self.client.exists(key))

    def expire(self, key: str, seconds: int) -> bool:
        """키 만료 시간 설정"""
        return bool(self.client.expire(key, seconds))

    def ttl(self, key: str) -> int:
        """키 만료 시간 조회"""
        return self.client.ttl(key)

    def ping(self) -> bool:
        """Redis 연결 상태 확인"""
        try:
            return self.client.ping()
        except:
            return False


# 전역 Redis 클라이언트 인스턴스
redis_client = RedisClient()
