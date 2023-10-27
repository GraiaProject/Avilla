from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal, overload

from avilla.qqapi.exception import (
    ActionFailed,
    ApiNotAvailable,
    AuditException,
    RateLimitException,
    UnauthorizedException,
)


@overload
def validate_response(data: Any, code: int, raising: Literal[False]) -> Any | Exception:
    ...


@overload
def validate_response(data: Any, code: int, raising: Literal[True] = True) -> Any:
    ...


def validate_response(data: dict, code: int, raising: bool = True):
    if code == 200 or 203 <= code < 300:
        return data.get("data", data)
    if code in {201, 202}:
        if data and (audit_id := data.get("data", {}).get("message_audit", {}).get("audit_id")):
            exc = AuditException(audit_id)
        else:
            exc = ActionFailed(code, data)
    elif code == 401:
        exc = UnauthorizedException(code, data)
    elif code in {404, 405}:
        exc = ApiNotAvailable(code, data)
    elif code == 429:
        exc = RateLimitException(code, data)
    else:
        exc = ActionFailed(code, data)
    if raising:
        raise exc
    return exc


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
