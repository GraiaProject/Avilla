from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from yarl import URL


@dataclass
class OneBot12Config:
    endpoint: URL
    access_token: str | None = None
    accounts: set[str] | None = None  # None 表示接受所有的账号类型.
    extra: Literal["allow", "warn", "close"] = "warn"
    msgpack: bool = False


# 似乎所有连接都要考虑用户限制和 msgpack. 如果以后各个连接有什么特殊的配置项再说吧.
OneBot12HttpClientConfig = OneBot12Config
OneBot12WebsocketClientConfig = OneBot12Config
OneBot12HttpServerConfig = OneBot12Config
OneBot12WebsocketServerConfig = OneBot12Config
