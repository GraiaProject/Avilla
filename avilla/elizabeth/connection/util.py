from __future__ import annotations

from enum import Enum
from typing import Any, Literal, overload

from avilla.core.exceptions import (
    AccountMuted,
    InvalidOperation,
    NetworkError,
    TooLongMessage,
    UnknownError,
    UnknownTarget,
)
from avilla.elizabeth.exception import (
    AccountNotFound,
    InvalidSession,
    InvalidVerifyKey,
    UnVerifiedSession,
)

code_exceptions_mapping: dict[int, type[Exception]] = {
    1: InvalidVerifyKey,
    2: AccountNotFound,
    3: InvalidSession,
    4: UnVerifiedSession,
    5: UnknownTarget,
    6: FileNotFoundError,
    10: PermissionError,
    20: AccountMuted,
    30: TooLongMessage,
    400: InvalidOperation,
    500: NetworkError,
}


@overload
def validate_response(data: Any, raising: Literal[False]) -> Any | Exception:
    ...


@overload
def validate_response(data: Any, raising: Literal[True] = True) -> Any:
    ...


def validate_response(data: dict, raising: bool = True):
    int_code = data.get("code") if isinstance(data, dict) else data
    if not isinstance(int_code, int) or int_code == 200 or int_code == 0:
        return data.get("data", data)
    exc_cls = code_exceptions_mapping.get(int_code)
    exc = exc_cls(exc_cls.__doc__, data) if exc_cls else UnknownError(data)
    if raising:
        raise exc
    return exc


CallMethod = Literal["get", "post", "fetch", "update", "multipart"]


class UploadMethod(str, Enum):
    """用于向 `upload` 系列方法描述上传类型"""

    Friend = "friend"
    """好友"""

    Group = "group"
    """群组"""

    Temp = "temp"
    """临时消息"""

    def __str__(self) -> str:
        return self.value


def camel_to_snake(name: str) -> str:
    if "_" in name:
        return name
    import re

    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", name)
    name = name.replace("-", "_").lower()
    return name


def snake_to_camel(name: str, capital: bool = False) -> str:
    name = "".join(seg.capitalize() for seg in name.split("_"))
    if not capital:
        name = name[0].lower() + name[1:]
    return name
