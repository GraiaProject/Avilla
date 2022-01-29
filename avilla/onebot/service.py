import asyncio
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, AsyncGenerator, Dict, List, Optional, Type, cast

from avilla.core.config import ConfigApplicant, ConfigFlushingMoment
from avilla.core.operator import ResourceOperator
from avilla.core.resource import ResourceProvider
from avilla.core.selectors import entity as entity_selector
from avilla.core.service import Service
from avilla.core.service.entity import ExportInterface, Status
from avilla.io.common.http import (
    HttpClient,
    HttpServer,
    WebsocketClient,
    WebsocketServer,
)
from avilla.onebot.accessors import OnebotImageAccessor
from avilla.onebot.config import (
    OnebotConnectionConfig,
    OnebotHttpClientConfig,
    OnebotHttpServerConfig,
    OnebotWsClientConfig,
    OnebotWsServerConfig,
)
from avilla.onebot.connection import OnebotConnection, OnebotWsClient
from avilla.core.selectors import resource as resource_selector

if TYPE_CHECKING:
    from avilla.core import Avilla

    from .protocol import OnebotProtocol


class OnebotInterface(ExportInterface):
    service: "OnebotService"

    def __init__(self, service: "OnebotService") -> None:
        self.service = service


class OnebotService(ConfigApplicant[OnebotConnectionConfig], Service, ResourceProvider):
    init_moment = {OnebotConnectionConfig: ConfigFlushingMoment.before_mainline}
    config_model = OnebotConnectionConfig
    supported_resource_types = {"image"}

    supported_interface_types = {OnebotInterface}
    status: Dict[entity_selector, Status]
    protocol: "OnebotProtocol"

    # http_client: Optional[HttpClient] = None
    # http_server: Optional[HttpServer] = None
    websocket_client: Optional[WebsocketClient] = None
    websocket_server: Optional[WebsocketServer] = None

    accounts: Dict[entity_selector, OnebotConnection]

    def __init__(self, protocol: "OnebotProtocol"):
        self.status = {}
        self.accounts = {}
        self.protocol = protocol

    def get_interface(self, interface_type: Type[OnebotInterface]) -> OnebotInterface:
        return OnebotInterface(self)

    def get_status(self, account: Optional[entity_selector] = None):
        if not account:
            return self.status
        if account not in self.status:
            raise ValueError(f"Account {account} not found")
        return self.status[account]

    async def launch_mainline(self, avilla: "Avilla"):
        loop = asyncio.get_running_loop()
        accounts = cast(List[entity_selector], avilla.get_config_scopes(self))
        if not accounts:
            raise ValueError("No accounts configured")
        assert all(
            isinstance(account, entity_selector) for account in accounts
        ), "Accounts must be entity selectors"
        tasks = []
        for account in accounts:
            conf = cast(OnebotConnectionConfig, avilla.get_config(self, account))
            if isinstance(conf, OnebotWsClientConfig):
                self.websocket_client = avilla.get_interface(WebsocketClient)
                connection = OnebotWsClient(self.websocket_client, account, self, conf)
                self.accounts[account] = connection
                tasks.append(loop.create_task(connection.maintask()))
            elif isinstance(conf, OnebotWsServerConfig):
                self.websocket_server = avilla.get_interface(WebsocketServer)
                # TODO: OnebotWsServer
            else:
                raise ValueError(f"{type(conf)} is not supported now.")

    @asynccontextmanager
    async def access_resource(self, res: resource_selector) -> AsyncGenerator["ResourceOperator", None]:
        if res.resource_type == "image":
            yield OnebotImageAccessor(self, res)
        raise NotImplementedError(f"Resource {res} is not supported")