from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Optional

from graia.amnesia.transport.common.status import (
    ConnectionStatus as BaseConnectionStatus,
)
from launart import ExportInterface, Launchable, LaunchableStatus
from loguru import logger
from statv import Stats

from avilla.spec.core.application import AccountAvailable, AccountUnavailable

from .config import HttpClientConfig, HttpServerConfig, T_Config
from .config import U_Config as U_Config
from .config import WebsocketClientConfig, WebsocketServerConfig
from .util import CallMethod, camel_to_snake

if TYPE_CHECKING:
    from ..protocol import ElizabethProtocol


class ConnectionStatus(BaseConnectionStatus, LaunchableStatus):
    """连接状态"""

    alive = Stats[bool]("alive", default=False)

    def __init__(self) -> None:
        self._session_key: Optional[str] = None
        super().__init__()

    @property
    def session_key(self) -> Optional[str]:
        return self._session_key

    @session_key.setter
    def session_key(self, value: Optional[str]) -> None:
        self._session_key = value
        self.connected = value is not None

    @property
    def available(self) -> bool:
        return bool(self.connected and self.session_key and self.alive)

    def __repr__(self) -> str:
        return "<ConnectionStatus {}>".format(
            " ".join(
                [
                    f"connected={self.connected}",
                    f"alive={self.alive}",
                    f"verified={self.session_key is not None}",
                    f"stage={self.stage}",
                ]
            )
        )


class ElizabethConnection(Launchable, Generic[T_Config]):
    status: ConnectionStatus
    protocol: ElizabethProtocol
    config: T_Config
    dependencies: frozenset[str | type[ExportInterface]]

    http_conn: Optional["HttpClientConnection"]

    @property
    def required(self):
        return set(self.dependencies)

    @property
    def stages(self):
        return set()

    def register_account(self):
        # NOTE: for hot registration
        # FIXME: require testing

        if self.account not in self.protocol.avilla.accounts:
            self.protocol.avilla.add_account(self.account)
            logger.success(
                f"Registered account: {self.config.account}",
                alt=f"[green]Registered account: [magenta]{self.config.account}[/]",
            )

    def on_connected_update(self, statv: ConnectionStatus, stats: Stats[bool], past: bool, current: bool) -> None:
        if past != current:
            logger.warning(f"Account({self.account.id}): {'Connected' if current else 'Disconnected'}")
            proto = self.account.protocol
            proto.avilla.broadcast.postEvent(
                (AccountAvailable if current else AccountUnavailable)(proto.avilla, self.account)
            )

    def __init__(self, protocol: ElizabethProtocol, config: T_Config) -> None:
        from avilla.elizabeth.account import ElizabethAccount

        from .http import HttpClientConnection

        self.id = ".".join(
            [
                "elizabeth",
                "connection",
                str(config.account),
                camel_to_snake(self.__class__.__qualname__),
            ]
        )
        self.protocol = protocol
        self.config = config
        self.status = ConnectionStatus()
        self.status.on_update(ConnectionStatus.connected)(self.on_connected_update)
        if config.use_http:
            self.http_conn = HttpClientConnection(protocol, HttpClientConfig.cast(config))
            self.http_conn.is_hook = True
            self.http_conn.status = self.status
            self.dependencies |= self.http_conn.dependencies
        else:
            self.http_conn = None
        self.account = ElizabethAccount(self.config.account, self.protocol)

    async def call(self, command: str, method: CallMethod, params: Optional[dict] = None) -> Any:
        if self.http_conn:
            return await self.http_conn.call(command, method, params)
        raise NotImplementedError(
            f"Connection {self} can't perform {command!r}, consider configuring a HttpClientConnection?"
        )


from .http import HttpClientConnection, HttpServerConnection  # noqa: E402
from .ws import WebsocketClientConnection, WebsocketServerConnection  # noqa: E402

CONFIG_MAP: dict[type[U_Config], type[ElizabethConnection]] = {
    HttpClientConfig: HttpClientConnection,
    HttpServerConfig: HttpServerConnection,
    WebsocketClientConfig: WebsocketClientConnection,
    WebsocketServerConfig: WebsocketServerConnection,
}
