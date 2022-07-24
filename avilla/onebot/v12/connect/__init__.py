from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Generic, Optional, Set, Type

from graia.amnesia.transport.common.status import ConnectionStatus as BaseConnectionStatus
from launart import ExportInterface, Launchable, LaunchableStatus
from statv import Stats
from typing_extensions import Self

from avilla.core.utilles.selector import Selector
from avilla.onebot.v12.connect.config import OneBotConfig

if TYPE_CHECKING:
    from ..protocol import OneBot12Protocol
    from ..service import ElizabethService


class ConnectionStatus(BaseConnectionStatus, LaunchableStatus):
    """连接状态"""

    @property
    def available(self) -> bool:
        return self.connected

    def __repr__(self) -> str:
        return "<ConnectionStatus {}>".format(
            " ".join(
                [
                    f"connected={self.connected}",
                    f"stage={self.stage}",
                ]
            )
        )

class OneBot12Connection(Launchable):
    status: ConnectionStatus
    protocol: OneBot12Protocol
    config: OneBotConfig

    def __init__(self, protocol: OneBot12Protocol, config: OneBotConfig) -> None:
        self.status = ConnectionStatus()
        self.protocol = protocol
        self.config = config

    @abstractmethod
    async def call_api(self, method: str, params: Any) -> Any:
        ...
