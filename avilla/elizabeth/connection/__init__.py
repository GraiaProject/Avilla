from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Generic, Optional, Set, Type

from graia.amnesia.transport.common.status import (
    ConnectionStatus as BaseConnectionStatus,
)
from launart import ExportInterface, Launchable, LaunchableStatus
from statv import Stats
from typing_extensions import Self

from avilla.core.utilles.selector import Selector

from ._info import (
    HttpClientInfo,
    HttpServerInfo,
    T_Info,
    U_Info,
    WebsocketClientInfo,
    WebsocketServerInfo,
)
from .util import CallMethod, camel_to_snake

if TYPE_CHECKING:
    from ..protocol import ElizabethProtocol
    from ..service import ElizabethService


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


class ElizabethConnection(Launchable, Generic[T_Info]):
    status: ConnectionStatus
    protocol: ElizabethProtocol
    config: T_Info
    dependencies: Set[str]

    fallback: Optional["HttpClientConnection"]

    @property
    def account(self) -> Selector:
        return Selector().land(self.protocol.land.name).account(str(self.config.account))  # type: ignore

    @property
    def required(self) -> Set[str]:
        return self.dependencies

    @property
    def stages(self):
        return {}

    def __init__(self, protocol: ElizabethProtocol, config: T_Info) -> None:
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
        self.fallback = None
        self.status = ConnectionStatus()

    async def call(self, command: str, method: CallMethod, params: Optional[dict] = None) -> Any:
        if self.fallback:
            return await self.fallback.call(command, method, params)
        raise NotImplementedError(
            f"Connection {self} can't perform {command!r}, consider configuring a HttpClientConnection?"
        )


from .http import HttpClientConnection, HttpServerConnection  # noqa: E402
from .ws import WebsocketClientConnection, WebsocketServerConnection  # noqa: E402

CONFIG_MAP: Dict[Type[U_Info], Type[ElizabethConnection]] = {
    HttpClientInfo: HttpClientConnection,
    HttpServerInfo: HttpServerConnection,
    WebsocketClientInfo: WebsocketClientConnection,
    WebsocketServerInfo: WebsocketServerConnection,
}


class ConnectionInterface(ExportInterface["ElizabethService"]):
    """Elizabeth 连接接口"""

    service: "ElizabethService"
    connection: Optional[ElizabethConnection]

    def __init__(self, service: "ElizabethService", account: Optional[int] = None) -> None:
        self.service = service
        self.connection = None
        if account:
            if not service.has_account(account):
                raise ValueError(f"Account {account} not found")
            self.connection = service.get_account(account)

    def bind(self, account: int) -> Self:
        """绑定账号, 返回一个新实例

        Args:
            account (int): 账号

        Returns:
            ConnectionInterface: 新实例
        """
        return ConnectionInterface(self.service, account)

    async def _call(self, command: str, method: CallMethod, params: dict, *, account: Optional[int] = None) -> Any:
        connection = self.connection
        if account is not None:
            connection = self.service.get_conn(account)
        if connection is None:
            raise ValueError(f"Unable to find connection to execute {command}")
        return await connection.call(command, method, params)

    async def call(
        self,
        command: str,
        method: CallMethod,
        params: dict,
        *,
        account: Optional[int] = None,
        in_session: bool = True,
    ) -> Any:
        """发起一个调用

        Args:
            command (str): 调用命令
            method (CallMethod): 调用方法
            params (dict): 调用参数
            account (Optional[int], optional): 账号. Defaults to None.
            in_session (bool, optional): 是否在会话中. Defaults to True.

        Returns:
            Any: 调用结果
        """
        if in_session:
            await self.status.wait_for_available()  # wait until session_key is present
            session_key = self.status.session_key
            params["sessionKey"] = session_key
        return await self._call(command, method, params, account=account)

    @property
    def status(self) -> ConnectionStatus:
        """获取连接状态"""
        if self.connection:
            return self.connection.status
        raise ValueError(f"{self} is not bound to an account")
