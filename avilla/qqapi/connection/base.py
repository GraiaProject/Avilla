from __future__ import annotations

import asyncio
from contextlib import suppress
from datetime import datetime, timezone, timedelta
from typing import TYPE_CHECKING, AsyncIterator, Literal, cast

from loguru import logger
from typing_extensions import Self
from aiohttp import ClientSession, FormData

from avilla.core.ryanvk.staff import Staff
from avilla.qqapi.audit import MessageAudited, audit_result
from avilla.qqapi.capability import QQAPICapability

from .util import Opcode, Payload, validate_response
from ..exception import NetworkError, UnauthorizedException

if TYPE_CHECKING:
    from avilla.qqapi.protocol import QQAPIProtocol, QQAPIConfig

CallMethod = Literal["get", "post", "fetch", "update", "multipart", "put", "delete", "patch"]


class QQAPINetworking:
    protocol: QQAPIProtocol
    close_signal: asyncio.Event
    session: ClientSession

    _access_token: str | None
    _expires_in: datetime | None

    def __init__(self, protocol: QQAPIProtocol, config: QQAPIConfig, app_id: str, secret: str):
        super().__init__()
        self.protocol = protocol
        self.config = config
        self.app_id = app_id
        self.secret = secret
        self._access_token = None
        self._expires_in = None

    def get_staff_components(self):
        return {"connection": self, "protocol": self.protocol, "avilla": self.protocol.avilla}

    def get_staff_artifacts(self):
        return [self.protocol.artifacts, self.protocol.avilla.global_artifacts]

    @property
    def staff(self):
        return Staff(self.get_staff_artifacts(), self.get_staff_components())

    def message_receive(self, shard: tuple[int, int]) -> AsyncIterator[tuple[Self, dict]]:
        ...

    @property
    def alive(self) -> bool:
        ...

    async def wait_for_available(self):
        ...

    async def send(self, payload: dict, shard: tuple[int, int]) -> None:
        ...

    async def message_handle(self, shard: tuple[int, int]):
        async for connection, data in self.message_receive(shard):
            if data["op"] != Opcode.DISPATCH:
                logger.debug(f"received other payload: {data}")
                continue
            payload = Payload(**data)
            connection.sequence = payload.sequence  # type: ignore

            async def event_parse_task(_data: Payload):
                event_type = _data.type
                if not event_type:
                    raise ValueError("event type is None")
                with suppress(NotImplementedError):
                    event = await QQAPICapability(connection.staff).event_callback(event_type.lower(), _data.data)
                    if event is not None:
                        if isinstance(event, MessageAudited):
                            audit_result.add_result(event)
                        await self.protocol.post_event(event)  # type: ignore
                    return
                logger.warning(f"received unsupported event {event_type.lower()}: {_data.data}")
                return

            asyncio.create_task(event_parse_task(payload))

    async def connection_closed(self):
        self.close_signal.set()

    async def _call_http(
        self, method: CallMethod, action: str, headers: dict[str, str] | None = None, params: dict | None = None
    ) -> dict:
        params = params or {}
        params = {k: v for k, v in params.items() if v is not None}
        if method in {"get", "fetch"}:
            async with self.session.get(
                (self.config.get_api_base() / action).with_query(params),
                headers=headers,
            ) as resp:
                return await validate_response(resp)

        if method == "patch":
            async with self.session.patch(
                (self.config.get_api_base() / action),
                json=params,
                headers=headers,
            ) as resp:
                return await validate_response(resp)

        if method == "put":
            async with self.session.put(
                (self.config.get_api_base() / action),
                json=params,
                headers=headers,
            ) as resp:
                return await validate_response(resp)

        if method == "delete":
            async with self.session.delete(
                (self.config.get_api_base() / action).with_query(params),
                headers=headers,
            ) as resp:
                return await validate_response(resp)

        if method in {"post", "update"}:
            async with self.session.post(
                (self.config.get_api_base() / action),
                json=params,
                headers=headers,
            ) as resp:
                return await validate_response(resp)

        if method == "multipart":
            if params is None:
                raise TypeError("multipart requires params")
            data = FormData(params["data"], quote_fields=False)
            for k, v in params["files"].items():
                if isinstance(v, dict):
                    data.add_field(k, v["value"], filename=v.get("filename"), content_type=v.get("content_type"))
                else:
                    data.add_field(k, v)

            async with self.session.post(
                (self.config.get_api_base() / action),
                data=data,
                headers=headers,
            ) as resp:
                return await validate_response(resp)

        raise ValueError(f"unknown method {method}")

    async def call_http(self, method: CallMethod, action: str, params: dict | None = None) -> dict:
        headers = await self.get_authorization_header()
        try:
            return await self._call_http(method, action, headers, params)
        except UnauthorizedException as e:
            self._access_token = None
            try:
                headers = await self.get_authorization_header()
            except Exception:
                raise e from None
            try:
                return await self._call_http(method, action, headers, params)
            except Exception as e1:
                raise e1 from None

    async def get_access_token(self) -> str:
        if self._access_token is None or (
            self._expires_in and datetime.now(timezone.utc) > self._expires_in - timedelta(seconds=30)
        ):
            async with self.session.post(
                self.config.get_auth_base(),
                json={
                    "appId": self.app_id,
                    "clientSecret": self.secret,
                },
            ) as resp:
                if resp.status != 200 or not resp.content:
                    raise NetworkError(
                        f"Get authorization failed with status code {resp.status}." " Please check your config."
                    )
                data = await resp.json()
            self._access_token = cast(str, data["access_token"])
            self._expires_in = datetime.now(timezone.utc) + timedelta(seconds=int(data["expires_in"]))
        return self._access_token

    async def _get_authorization_header(self) -> str:
        """获取当前 Bot 的鉴权信息"""
        # if self.config.is_group_bot:
        return f"QQBot {await self.get_access_token()}"
        # return f"Bot {self.config.id}.{self.config.token}"

    async def get_authorization_header(self) -> dict[str, str]:
        """获取当前 Bot 的鉴权信息"""
        return {"Authorization": await self._get_authorization_header()}
