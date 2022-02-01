import asyncio
import hmac
import json
from contextlib import ExitStack, asynccontextmanager
from typing import (
    TYPE_CHECKING,
    AsyncGenerator,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    Union,
    cast,
    overload,
)

from loguru import logger
from starlette.responses import JSONResponse

from avilla.core.config import ConfigApplicant, ConfigFlushingMoment
from avilla.core.context import ctx_avilla, ctx_protocol, ctx_relationship
from avilla.core.launch import LaunchComponent
from avilla.core.operator import ResourceOperator
from avilla.core.resource import ResourceProvider
from avilla.core.selectors import entity as entity_selector
from avilla.core.selectors import resource as resource_selector
from avilla.core.service import Service
from avilla.core.service.entity import ExportInterface, Status
from avilla.core.stream import Stream
from avilla.core.transformers import u8_string
from avilla.io.common.http import (
    HttpClient,
    HttpServer,
    HttpServerRequest,
    WebsocketClient,
    WebsocketConnection,
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
from avilla.onebot.connection import (
    OnebotConnection,
    OnebotConnectionRole,
    OnebotHttpClient,
    OnebotHttpServer,
    OnebotWsClient,
    OnebotWsServer,
)
from avilla.onebot.utilles import raise_for_obresp

from .interface import OnebotInterface

if TYPE_CHECKING:
    from avilla.core import Avilla

    from .protocol import OnebotProtocol

EllipsisType = type(...)


class OnebotService(ConfigApplicant[OnebotConnectionConfig], Service, ResourceProvider):
    init_moment = {OnebotConnectionConfig: ConfigFlushingMoment.before_mainline}
    config_model = OnebotConnectionConfig
    supported_resource_types = {"image"}

    supported_interface_types = {OnebotInterface}
    status: Dict[entity_selector, Status]
    protocol: "OnebotProtocol"

    http_client: Optional[HttpClient] = None
    http_server: Optional[HttpServer] = None
    websocket_client: Optional[WebsocketClient] = None
    websocket_server: Optional[WebsocketServer] = None

    accounts: Dict[entity_selector, Dict[OnebotConnectionRole, OnebotConnection]]

    def __init__(self, protocol: "OnebotProtocol"):
        self.status = {}
        self.accounts = {}
        self.available_waiters = {}
        self.protocol = protocol

    def get_interface(self, interface_type: Type[OnebotInterface]) -> OnebotInterface:
        return OnebotInterface(self)

    if TYPE_CHECKING:
        @overload
        def get_status(self) -> Dict[entity_selector, Status]:
            ...
        
        @overload
        def get_status(self, account: entity_selector) -> Status:
            ...

    def get_status(self, account: Optional[entity_selector] = None):
        if not account:
            return self.status
        if account not in self.status:
            raise ValueError(f"Account {account} not found")
        return self.status[account]

    async def launch_mainline(self, avilla: "Avilla"):
        loop = asyncio.get_running_loop()
        accounts = cast(List[Union[entity_selector, EllipsisType]], avilla.get_config_scopes(self.__class__))
        if not accounts:
            raise ValueError("No accounts configured")
        assert all(
            isinstance(account, entity_selector) for account in accounts if account is not ...
        ), "Accounts must be entity selectors"
        tasks = []
        for account in accounts:
            if isinstance(account, EllipsisType):
                continue
            conf = cast(OnebotConnectionConfig, avilla.get_config(self.__class__, account))
            conns = self.accounts.setdefault(account.without_group(), {})
            self.set_status(account.without_group(), False, "non-configured")
            if isinstance(conf, OnebotWsClientConfig):
                self.websocket_client = avilla.get_interface(WebsocketClient)
                ob_ws_client = OnebotWsClient(self.websocket_client, account, self, conf)
                if "event" in conns and "action" in conns:
                    raise ValueError(
                        f"Account {account} already configured event method and action method, ws method is unnecessary"
                    )
                if "event" not in conns:
                    conns["event"] = ob_ws_client
                    tasks.append(loop.create_task(ob_ws_client.maintask()))
                if "action" not in conns:
                    conns["action"] = ob_ws_client
                if conns.get("event") is ob_ws_client and conns.get("action") is ob_ws_client:
                    conns['universal'] = ob_ws_client
            elif isinstance(conf, OnebotWsServerConfig):
                self.websocket_server = avilla.get_interface(WebsocketServer)
                ob_ws_server = OnebotWsServer(self.websocket_server, account, self, conf)
                tasks.append(loop.create_task(ob_ws_server.maintask()))
                if "event" in conns and "action" in conns:
                    raise ValueError(
                        f"Account {account} already configured event method and action method, ws-reverse method is unnecessary"
                    )
                if "action" not in conns:
                    conns["action"] = ob_ws_server
                if "event" not in conns:
                    conns["event"] = ob_ws_server
                if conns.get("event") is ob_ws_server and conns.get("action") is ob_ws_server:
                    conns["universal"] = ob_ws_server
            elif isinstance(conf, OnebotHttpClientConfig):
                self.http_client = avilla.get_interface(HttpClient)
                ob_http_client = OnebotHttpClient(self.http_client, account, self, conf)
                tasks.append(loop.create_task(ob_http_client.maintask()))
                if "action" in conns:
                    raise ValueError(
                        f"Account {account} already configured action method, http method is unnecessary"
                    )
                conns["action"] = ob_http_client
            elif isinstance(conf, OnebotHttpServerConfig):
                self.http_server = avilla.get_interface(HttpServer)
                ob_http_server = OnebotHttpServer(self.http_server, account, self, conf)
                tasks.append(loop.create_task(ob_http_server.maintask()))
                if "event" in conns:
                    raise ValueError(
                        f"Account {account} already configured event method, http method is unnecessary"
                    )
                conns["event"] = ob_http_server
            else:
                raise ValueError(f"{type(conf)} is not supported now.")
        for account in accounts:
            if isinstance(account, EllipsisType):
                continue
            conns = self.accounts[account.without_group()]
            if "event" not in conns and "action" not in conns:
                raise ValueError(f"Account {account} not configured event and action method")
            if "event" not in conns:
                raise ValueError(f"Account {account} not configured event method")
            if "action" not in conns:
                raise ValueError(f"Account {account} not configured action method")
        await asyncio.gather(*tasks)

    @asynccontextmanager
    async def access_resource(self, res: resource_selector) -> AsyncGenerator["ResourceOperator", None]:
        if res.resource_type == "image":
            yield OnebotImageAccessor(self, res)
        raise NotImplementedError(f"Resource {res} is not supported")

    @property
    def launch_component(self) -> LaunchComponent:
        return LaunchComponent("avilla.onebot.service", {"http.universal_client"}, self.launch_mainline)

    async def http_server_on_received(self, request: HttpServerRequest):
        headers = await request.headers()
        data = await request.read()
        account = entity_selector.account[headers["X-Self-ID"]]
        if account not in self.accounts:
            return request.response({"error": f"Account {headers['X-Self-ID']} not found"}, status=204)
        conn = self.accounts[account]["event"]
        if (
            conn.config.access_token is None
            or headers["X-Signature"][5:]
            == hmac.new(conn.config.access_token.encode(), await data.unwrap(), "sha1").hexdigest()
        ):
            data = await data.transform(u8_string).transform(json.loads).unwrap()
            raise_for_obresp(data)
            event = await self.protocol.parse_event(data)
            if event:
                with ExitStack() as stack:
                    stack.enter_context(ctx_avilla.use(self.protocol.avilla))
                    stack.enter_context(ctx_protocol.use(self.protocol))
                    self.protocol.avilla.broadcast.postEvent(event)

    async def ws_server_before_accept(self, srv: OnebotWsServer, conn: WebsocketConnection):
        headers = conn.headers()
        account = entity_selector.account[headers["x-self-id"]]
        if account not in self.accounts:
            await conn.close()
            return
        role = cast(
            OnebotConnectionRole,
            {"API": "action", "Event": "event", "Universal": "universal"}[headers["x-client-role"]],
        )
        config = srv.config
        if config.access_token is not None:
            logger.warning(f"you set access_token for a reverse ws, but it's unused by the internal logic")
        client = cast(Tuple[str, int], conn.client)
        conns = self.accounts[account]
        # 大问题。。主要还是得看 user conf.
        logger.info(f"{account} connected by {client[0]}:{client[1]}, act as {role}")
        if role == "universal":
            if conns.get("universal") is not srv:
                logger.warning(f"{account} already configured as universal but in another way, close the current connection")
                await conn.close()
                return
            conns[cast(OnebotConnectionRole, "universal")] = srv

            if "action" not in conns:
                conns["action"] = srv
            else:
                if conns['action'] is not srv:
                    logger.warning(
                        f"{account} already has action method but in another way, reverse-ws method is unnecessary, so it will be ignored"
                    )
                    await conn.close()

            if "event" not in conns:
                conns["event"] = srv
            else:
                if conns['event'] is not srv:
                    logger.warning(
                        f"{account} already has event method but in another way, reverse-ws method is unnecessary, so it will be ignored"
                    )
                    await conn.close()

    async def ws_server_on_connected(self, srv: OnebotWsServer, conn: WebsocketConnection):
        headers = conn.headers()
        account = entity_selector.account[headers["x-self-id"]]
        self.set_status(account, True, "ok")
        self.trig_available_waiters(account)

    async def ws_server_on_close(self, srv: OnebotWsServer, conn: WebsocketConnection):
        headers = conn.headers()
        account = entity_selector.account[headers["x-self-id"]]
        self.set_status(account, False, "closed")

    async def ws_server_on_received(
        self, srv: OnebotWsServer, conn: WebsocketConnection, stream: Stream[Union[bytes, str, dict, list]]
    ):
        data = (
            await stream.transform(u8_string, bytes)  # type: ignore
            .transform(cast(Callable[[str], Dict], srv.config.data_parser), str)
            .unwrap()
        )
        if "echo" in data:
            logger.debug(f"received echo: {data}")
            if data["echo"] in srv.requests:
                srv.requests[data["echo"]].set_result(data)
            else:
                logger.warning(f"Received echo message {data['echo']} but not found in requests: {data}")
        else:
            # logger.debug(f"received event: {data}")
            event = await self.protocol.parse_event(data)
            if event:
                with ExitStack() as stack:
                    stack.enter_context(ctx_avilla.use(self.protocol.avilla))
                    stack.enter_context(ctx_protocol.use(self.protocol))
                    self.protocol.avilla.broadcast.postEvent(event)
