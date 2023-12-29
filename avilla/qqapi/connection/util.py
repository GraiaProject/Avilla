from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal

from aiohttp import ClientResponse

from avilla.qqapi.exception import (
    ActionFailed,
    ApiNotAvailable,
    AuditException,
    RateLimitException,
    UnauthorizedException,
)


async def validate_response(resp: ClientResponse):
    status = resp.status
    if status == 200 or 203 <= status < 300:
        data = await resp.json()
        return data.get("data", data)
    if status in {201, 202}:
        data = await resp.json()
        if data and (audit_id := data.get("data", {}).get("message_audit", {}).get("audit_id")):
            exc = AuditException(audit_id)
        else:
            exc = ActionFailed(status, resp.headers, await resp.text())
    elif status == 401:
        exc = UnauthorizedException(status, resp.headers, await resp.text())
    elif status in {404, 405}:
        exc = ApiNotAvailable(status, resp.headers, await resp.text())
    elif status == 429:
        exc = RateLimitException(status, resp.headers, await resp.text())
    else:
        exc = ActionFailed(status, resp.headers, await resp.text())
    raise exc


CallMethod = Literal["get", "post", "fetch", "update", "multipart"]


class Opcode(int, Enum):
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    RESUME = 6
    RECONNECT = 7
    INVALID_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11


@dataclass
class Payload:
    op: int | Opcode
    d: dict | None = None
    s: int | None = None
    t: str | None = None
    id: str | None = None

    @property
    def opcode(self) -> Opcode:
        return Opcode(self.op)

    @property
    def data(self) -> dict:
        return self.d or {}

    @property
    def sequence(self) -> int | None:
        return self.s

    @property
    def type(self) -> str | None:
        return self.t
