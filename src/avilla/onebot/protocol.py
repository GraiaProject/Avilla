import asyncio
import contextlib
import json
from typing import Any, Dict, Final, List, Tuple, Type, Union

from avilla import context
from avilla.builtins.profile import FriendProfile, MemberProfile, SelfProfile
from avilla.context import ctx_protocol
from avilla.entity import Entity
from avilla.execution import Execution
from avilla.group import Group
from avilla.message.chain import MessageChain
from avilla.network.client import (AbstractHttpClient, AbstractWebsocketClient,
                                   Client)
from avilla.network.service import Service
from avilla.network.signatures import (ClientCommunicationMethod,
                                       ServiceCommunicationMethod)
from avilla.onebot.config import (HttpCommunication, OnebotConfig,
                                  ReverseWebsocketCommunication,
                                  WebsocketCommunication)
from avilla.onebot.element_tree import ELEMENT_TYPE_MAP
from avilla.platform import Platform
from avilla.protocol import BaseProtocol
from avilla.relationship import Relationship
from avilla.utilles import random_string
from avilla.utilles.transformer import JsonTransformer, Utf8StringTransformer

from .event_tree import EVENT_PARSING_TREE, gen_parsing_key
from .execution_ensure import ensure_execution
from .message_serializer import onebot_msg_serializer


class OnebotProtocol(BaseProtocol):
    config: OnebotConfig

    platform: Final[Platform] = Platform(
        name="Tencent QQ",
        protocol_provider_name="universal",
        implementation="OneBot",
        supported_impl_version="v11",
        generation="11",
    )

    _pending_futures: Dict[str, asyncio.Future]

    def __post_init__(self) -> None:
        self._pending_futures = {}

        if self.using_exec_method is WebsocketCommunication:
            ws_client: AbstractWebsocketClient = self.avilla.network_interface.get_network("ws")  # type: ignore
            ws_client.on_received_data(self.config.bot_id)(self._onebot_ws_data_received)

    def ensure_networks(
        self,
    ) -> Tuple[
        Dict[str, Union[Client, Service]],
        Union[Type[ClientCommunicationMethod], Type[ServiceCommunicationMethod]],
    ]:
        result = {}
        comm_method = None
        if "http" in self.config.communications:
            result["http"] = self.avilla.network_interface.get_network("http")
            comm_method = HttpCommunication
        if "http-service" in self.config.communications:
            result["http-service"] = self.avilla.network_interface.get_network("http-service")
        if "ws-service" in self.config.communications:
            result["ws-service"] = self.avilla.network_interface.get_network("ws-service")
            comm_method = ReverseWebsocketCommunication
        if "ws" in self.config.communications:
            result["ws"] = self.avilla.network_interface.get_network("ws")
            comm_method = WebsocketCommunication

        if result and comm_method:
            return result, comm_method
        else:
            raise TypeError("invaild config for network")

    def get_self(self) -> "Entity[SelfProfile]":
        return Entity(self.config.bot_id, SelfProfile())

    async def parse_message(self, data: List[Dict]) -> "MessageChain":
        result = []

        with ctx_protocol.use(self):
            for x in data:
                elem_type = x["type"]
                elem_parser = ELEMENT_TYPE_MAP.get(elem_type)
                if elem_parser:
                    result.append(await elem_parser(x["data"]))
                else:
                    self.avilla.logger.error(f"message_parser: unexpected element type {elem_type}")

        return MessageChain.create(result)

    async def serialize_message(self, message: "MessageChain") -> List:
        return await onebot_msg_serializer.serialize(message)

    async def get_relationship(
        self, entity: "Union[Entity[Union[MemberProfile, FriendProfile]], Group]"
    ) -> "Relationship[Union[MemberProfile, FriendProfile], OnebotProtocol]":
        return Relationship(entity, self)

    async def launch_entry(self):
        comms = self.config.communications
        if self.using_exec_method is WebsocketCommunication:
            ws_client: AbstractWebsocketClient = self.using_networks["ws"]  # type: ignore
            ws_config: WebsocketCommunication = comms["ws"]  # type: ignore
            await ws_client.connect(
                ws_config.api_root, account=self.config.bot_id, headers=self._get_http_headers()
            )

    async def ensure_execution(self, execution: Execution) -> Any:
        return await ensure_execution(self, execution=execution)

    def _get_http_headers(self):
        return {
            "Content-Type": "application/json",
            **(
                {"Authorization": f"Bearer {self.config.access_token}"}
                if self.config.access_token
                else {}
            ),
        }

    async def _http_get(self, path: str, params: Dict[str, str] = None) -> Any:
        http_client: AbstractHttpClient = self.using_networks["http"]  # type: ignore
        return (
            (
                await http_client.get(
                    self.config.communications["http"]
                    .api_root.with_path(path)  # type:ignore
                    .with_query(params or {}),
                    headers=self._get_http_headers(),
                )
            )
            .passby(Utf8StringTransformer)
            .passby(JsonTransformer)
            .transform()
        )

    async def _http_post(self, path: str, data: Union[Dict, Any]) -> Any:
        http_client: AbstractHttpClient = self.using_networks["http"]  # type: ignore
        return (
            (
                await http_client.post(
                    self.config.communications["http"].api_root.with_path(path),  # type:ignore
                    json=data,
                    headers=self._get_http_headers(),
                )
            )
            .passby(Utf8StringTransformer)
            .passby(JsonTransformer)
            .transform()
        )

    async def _ws_client_send_packet(self, action: str, data: Any) -> Any:
        ws_client: AbstractWebsocketClient = self.using_networks["ws"]  # type: ignore

        response_id: str = random_string()

        ftr = asyncio.get_running_loop().create_future()
        self._pending_futures[response_id] = ftr
        await ws_client.send_json(
            self.config.bot_id, {"action": action, "params": data, "echo": response_id}
        )
        return await ftr

    async def _onebot_send_packet(self, endpoint: str, data: Any) -> Any:
        if self.using_exec_method is WebsocketCommunication:
            return await self._ws_client_send_packet(endpoint, data)
        elif self.using_exec_method is HttpCommunication:
            return await self._http_post("/" + endpoint, data)

    async def _onebot_ws_data_received(self, client, connid, raw_data: Union[str, bytes]):
        if isinstance(raw_data, bytes):
            raw_data = raw_data.decode()
        data: Dict = json.loads(raw_data)
        is_event = "post_type" in data
        if is_event:
            event_parser = EVENT_PARSING_TREE.get(gen_parsing_key(data))  # ignore: noqa
            if event_parser:
                event = await event_parser(self, data)
                if event.__class__.__name__ != "HeartbeatReceived":  # Heartbeat
                    self.avilla.logger.debug(
                        f"received event [{event.__class__.__name__}]: {repr(event)}"
                    )
                else:
                    self.avilla.logger.debug("received heartbeat packet")
                with contextlib.ExitStack() as stack:
                    stack.enter_context(context.ctx_avilla.use(self.avilla))
                    stack.enter_context(context.ctx_event.use(event))
                    stack.enter_context(context.ctx_protocol.use(self))
                    self.avilla.broadcast.postEvent(event)
            else:
                self.avilla.logger.error(
                    f"event receiver: unknown event: key={gen_parsing_key(data)}, data={data}"
                )
        else:
            p_ftr = self._pending_futures.get(data["echo"])
            if p_ftr:
                p_ftr.set_result(data)
