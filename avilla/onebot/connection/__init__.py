from __future__ import annotations

from abc import ABCMeta, abstractclassmethod
from typing import TYPE_CHECKING, ClassVar, Generic, Literal, TypeVar

from graia.amnesia.transport.common.status import ConnectionStatus
from launart import ExportInterface, Launchable, LaunchableStatus

from .config import OneBot11Config

if TYPE_CHECKING:
    from ..account import OneBot11Account

C = TypeVar("C", bound=OneBot11Config)
I = TypeVar("I", bound=ExportInterface)


class OneBot11ConnectionStatus(ConnectionStatus, LaunchableStatus):
    pass


class OneBot11Connection(Launchable, Generic[C, I], metaclass=ABCMeta):
    required: ClassVar[set[str | type[ExportInterface]]]
    stages: ClassVar[set[Literal["preparing", "blocking", "cleanup"]]]

    account: OneBot11Account
    config: C
    interface: I
    status: OneBot11ConnectionStatus

    def __init__(self, account: OneBot11Account, config: C) -> None:
        self.id = ".".join(
            (
                "onebot11",
                "connection",
                account.id,
                self.id.split(".")[-1],
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
