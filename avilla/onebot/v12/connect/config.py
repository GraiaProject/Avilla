from __future__ import annotations 

from dataclasses import dataclass, field
from typing import Literal, Union

from yarl import URL


@dataclass
class OneBot12WebsocketClientConfig:
    endpoint: URL
    access_token: str | None = None
    accounts: list[str] | None = None # none 表示接受所有的账号类型.
    extra: Literal['allow', 'warn', 'close'] = "warn"

@dataclass
class OneBot12WebsocketServerConfig:
    endpoint: str
    access_token: str | None = None

OneBotConfig = Union[
    OneBot12WebsocketClientConfig,
    OneBot12WebsocketServerConfig
]
