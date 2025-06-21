import json
from collections.abc import Callable
from typing import Any

from nats.aio.client import Client as NatsClient
from nats.aio.msg import Msg

from .config import nats_config


class NatsClientWrapper:
    """NATS 클라이언트 래퍼"""

    def __init__(self):
        self.client = NatsClient()
        self._connected = False
        self._subscriptions: dict[str, Callable] = {}

    async def connect(self):
        """NATS 서버 연결"""
        if self._connected:
            return

        try:
            # 연결 옵션 설정
            options = {
                "servers": nats_config.servers,
                "name": nats_config.client_name,
                "reconnect_time_wait": nats_config.reconnect_time_wait,
                "max_reconnect_attempts": nats_config.max_reconnect_attempts,
                "ping_interval": nats_config.ping_interval,
                "max_outstanding_pings": nats_config.max_outstanding_pings,
            }

            # 인증 설정
            if nats_config.username and nats_config.password:
                options["user"] = nats_config.username
                options["password"] = nats_config.password
            elif nats_config.token:
                options["token"] = nats_config.token

            await self.client.connect(**options)
            self._connected = True

            # 연결 이벤트 핸들러 설정
            await self.client.subscribe(">", cb=self._message_handler)

        except Exception as e:
            raise Exception(f"NATS 연결 실패: {e}")

    async def disconnect(self):
        """NATS 서버 연결 해제"""
        if self._connected:
            await self.client.close()
            self._connected = False

    async def publish(self, subject: str, payload: Any, reply: str | None = None):
        """메시지 발행"""
        if not self._connected:
            await self.connect()

        if isinstance(payload, (dict, list)):
            payload = json.dumps(payload).encode()
        elif isinstance(payload, str):
            payload = payload.encode()

        await self.client.publish(subject, payload, reply=reply)

    async def subscribe(self, subject: str, callback: Callable):
        """메시지 구독"""
        if not self._connected:
            await self.connect()

        self._subscriptions[subject] = callback
        await self.client.subscribe(subject, cb=callback)

    async def request(
        self, subject: str, payload: Any, timeout: float = 1.0
    ) -> Msg | None:
        """요청-응답 패턴"""
        if not self._connected:
            await self.connect()

        if isinstance(payload, (dict, list)):
            payload = json.dumps(payload).encode()
        elif isinstance(payload, str):
            payload = payload.encode()

        try:
            response = await self.client.request(subject, payload, timeout=timeout)
            return response
        except TimeoutError:
            return None

    async def _message_handler(self, msg: Msg):
        """기본 메시지 핸들러"""
        subject = msg.subject
        data = msg.data.decode()

        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            pass

        # 구독된 핸들러가 있으면 호출
        if subject in self._subscriptions:
            await self._subscriptions[subject](msg)

    def is_connected(self) -> bool:
        """연결 상태 확인"""
        return self._connected and self.client.is_connected


# 전역 NATS 클라이언트 인스턴스
nats_client = NatsClientWrapper()
