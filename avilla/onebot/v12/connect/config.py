from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from yarl import URL


@dataclass
class OneBot12WebsocketClientConfig:
    endpoint: URL
    access_token: str | None = None
    account: str | None = None  # none 表示接受所有的账号类型.


@dataclass
class OneBot12WebsocketServerConfig:
    endpoint: str
    access_token: str | None = None
    account: str | None = None  # none 表示接受所有的账号类型.


OneBotConfig = Union[OneBot12WebsocketClientConfig, OneBot12WebsocketServerConfig]
