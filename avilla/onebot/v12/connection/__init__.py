from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Generic, Literal, Optional, Set, Type

from graia.amnesia.transport.common.status import ConnectionStatus
from launart import ExportInterface, Launchable, LaunchableStatus
from statv import Stats
from typing_extensions import Self

from avilla.core.utilles.selector import Selector

from ..account import OneBot12Account
from ..connection.config import OneBot12Config

if TYPE_CHECKING:
    from ..protocol import OneBot12Protocol


class OneBot12Connection(Launchable):
    status: ConnectionStatus
    protocol: OneBot12Protocol
    config: OneBot12Config
    accounts: dict[str, OneBot12Account]

    def __init__(self, protocol: OneBot12Protocol, config: OneBot12Config) -> None:
        self.status = ConnectionStatus()
        self.protocol = protocol
        self.config = config

    @abstractmethod
    async def call(self, action: str, params: Optional[dict] = None) -> Any:
        ...
