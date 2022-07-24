from __future__ import annotations

from abc import ABCMeta, abstractclassmethod
from typing import ClassVar, Generic, Literal, TypeVar

from graia.amnesia.transport.common.status import ConnectionStatus
from launart import Launchable, LaunchableStatus

from avilla.onebot.v11.account import OneBot11Account

from .config import OneBot11Config

T = TypeVar("T", bound=OneBot11Config)


class OneBot11ConnectionStatus(ConnectionStatus, LaunchableStatus):
    pass


class OneBot11Connection(Launchable, Generic[T], metaclass=ABCMeta):
    name: ClassVar[str]
    required: ClassVar[set[str]]
    stages: ClassVar[set[Literal["prepare", "blocking", "cleanup"]]]  # TODO: 明早问蓝块到底是preparing还是prepare

    account: OneBot11Account
    config: T
    status: OneBot11ConnectionStatus

    def __init__(self, account: OneBot11Account, config: T) -> None:
        self.id = ".".join(
            (
                "onebot11",
                "connection",
                account.id,
                self.name,
            )
        )
        self.account = account
        self.config = config
        self.status = OneBot11ConnectionStatus()

    @abstractclassmethod
    async def call(self, action: str, params: dict | None = None) -> dict | None:
        raise NotImplementedError


from .http import OneBot11HttpClientConnection as OneBot11HttpClientConnection
from .http import OneBot11HttpServerConnection as OneBot11HttpServerConnection
from .ws import OneBot11WebsocketClientConnection as OneBot11WebsocketClientConnection
from .ws import OneBot11WebsocketServerConnection as OneBot11WebsocketServerConnection
