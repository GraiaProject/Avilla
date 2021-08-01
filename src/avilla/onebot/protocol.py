import asyncio
import base64
import json
from typing import AsyncIterable, Dict, List, Tuple, Type, Union

from graia.broadcast.utilles import printer

from avilla import context
from avilla.builtins.elements import Image, Notice, NoticeAll, PlainText, Quote
from avilla.builtins.profile import FriendProfile, GroupProfile, MemberProfile, SelfProfile
from avilla.entity import Entity
from avilla.exceptions import ExecutionException
from avilla.execution.fetch import *
from avilla.execution.group import *
from avilla.execution.message import *
from avilla.execution.request import *
from avilla.group import Group
from avilla.message.chain import MessageChain
from avilla.network.client import AbstractHttpClient, AbstractWebsocketClient, Client
from avilla.network.service import Service
from avilla.network.signatures import ClientCommunicationMethod, ServiceCommunicationMethod
from avilla.onebot.config import HttpCommunication, OnebotConfig, ReverseWebsocketCommunication, WebsocketCommunication
from avilla.protocol import BaseProtocol
from avilla.provider import HttpGetProvider
from avilla.relationship import Relationship
from avilla.utilles import random_string
from avilla.utilles.transformer import JsonTransformer, Utf8StringTransformer
from avilla.utilles.override_bus import OverrideBus
from avilla.utilles.override_subbus import proto_ensure_exec_params, network_method_subbus, execution_subbus
from .event_tree import EVENT_PARSING_TREE, gen_parsing_key

from .resp import *

ELEMENT_TYPE_MAP = {
    "text": lambda x: PlainText(x["text"]),
    "image": lambda x: Image(HttpGetProvider(x["url"])),
    "at": lambda x: x["qq"] == "all" and NoticeAll() or Notice(str(x["qq"])),
    "reply": lambda x: Quote(id=x["id"]),
}


class OnebotProtocol(BaseProtocol):
    config: OnebotConfig

    _pending_futures: Dict[str, asyncio.Future]

    def __post_init__(self) -> None:
        self._pending_futures = {}

        if self.using_exec_method is WebsocketCommunication:
            ws_client: AbstractWebsocketClient = self.avilla.network_interface.get_network("ws")

            @ws_client.on_received_data(self.config.bot_id)
            async def onebot_ws_data_received(client, connid, raw_data: Union[str, bytes]):
                if isinstance(raw_data, bytes):
                    raw_data = raw_data.decode()
                data: Dict = json.loads(raw_data)
                is_event = "post_type" in data
                if is_event:
                    event_parser = EVENT_PARSING_TREE.get(gen_parsing_key(data))
                    if event_parser:
                        event = await event_parser(self, data)
                        with (
                            context.ctx_avilla.use(self.avilla),
                            context.ctx_event.use(event),
                            context.ctx_protocol.use(self),
                        ):
                            self.avilla.broadcast.postEvent(event)
                    else:
                        print("cannot parse event:", gen_parsing_key(data), data)
                else:
                    p_ftr = self._pending_futures.get(data["echo"])
                    if p_ftr:
                        p_ftr.set_result(data)

    def ensure_networks(
        self,
    ) -> Tuple[
        Dict[str, Union[Client, Service]], Union[Type[ClientCommunicationMethod], Type[ServiceCommunicationMethod]]
    ]:
        result = {}
        comm_method = None
        if "http" in self.config.communications:
            result["http"] = self.avilla.network_interface.get_network("http")
            comm_method = HttpCommunication
        if "ws" in self.config.communications:
            result["ws"] = self.avilla.network_interface.get_network("ws")
            comm_method = WebsocketCommunication
        if result:
            return result, comm_method

        if "http-service" in self.config.communications:
            result["http-service"] = self.avilla.network_interface.get_network("http-service")
        if "ws-service" in self.config.communications:
            result["ws-service"] = self.avilla.network_interface.get_network("ws-service")
            comm_method = ReverseWebsocketCommunication

        if result and comm_method:
            return result, comm_method
        else:
            raise TypeError("invaild config for network")

    def get_self(self) -> "Entity[SelfProfile]":
        return Entity(self.config.bot_id, SelfProfile())

    async def get_members(
        self, group: Group[GroupProfile]
    ) -> "AsyncIterable[Entity[Union[SelfProfile, MemberProfile]]]":
        return self.ensureExecution()

    async def parse_message(self, data: List[Dict]) -> "MessageChain":
        result = []

        for x in data:
            elem_type = x["type"]
            elem_parser = ELEMENT_TYPE_MAP.get(elem_type)
            if elem_parser:
                result.append(elem_parser(x["data"]))
            else:
                print("cannot parse elem:", elem_type)

        return MessageChain.create(result)

    async def serialize_message(self, message: "MessageChain") -> List:
        result = []

        for element in message.__root__:
            if isinstance(element, PlainText):
                result.append({"type": "text", "data": {"text": element.text}})
            elif isinstance(element, Image):
                result.append(
                    {
                        "type": "image",
                        "data": {
                            "file": f"base64://{base64.urlsafe_b64encode(await element.provider()).decode('utf-8')}"
                        },
                    }
                )
            elif isinstance(element, Notice):
                result.append({"type": "at", "data": {"qq": int(element.target)}})
            elif isinstance(element, NoticeAll):
                result.append({"type": "at", "data": {"qq": "all"}})

        return result

    async def get_relationship(
        self, entity: "Union[Entity[Union[MemberProfile, FriendProfile]], Group[GroupProfile]]"
    ) -> "Relationship[Union[MemberProfile, FriendProfile], GroupProfile, OnebotProtocol]":
        return Relationship(entity, self)

    async def launch_entry(self):
        comms = self.config.communications
        if self.using_exec_method is WebsocketCommunication:
            ws_client: AbstractWebsocketClient = self.using_networks["ws"]
            await ws_client.connect(comms["ws"].api_root, account=self.config.bot_id, headers=self._get_http_headers())

    def _get_http_headers(self):
        return {
            "Content-Type": "application/json",
            **({"Authorization": f"Bearer {self.config.access_token}"} if self.config.access_token else {}),
        }

    async def _http_get(self, path: str, params: Dict[str, str]) -> Any:
        http_client: AbstractHttpClient = self.using_networks["http"]
        return (
            (
                await http_client.get(
                    self.config.communications["http"].api_root.with_path(path).with_query(params),
                    headers=self._get_http_headers(),
                )
            )
            .passby(Utf8StringTransformer)
            .passby(JsonTransformer)
            .transform()
        )

    async def _http_post(self, path: str, data: Union[Dict, List]) -> Any:
        http_client: AbstractHttpClient = self.using_networks["http"]
        return (
            (
                await http_client.post(
                    self.config.communications["http"].api_root.with_path(path),
                    json=data,
                    headers=self._get_http_headers(),
                )
            )
            .passby(Utf8StringTransformer)
            .passby(JsonTransformer)
            .transform()
        )

    async def _ws_client_send_packet(self, action: str, data: Any) -> Any:
        ws_client: AbstractWebsocketClient = self.using_networks["ws"]

        response_id: str = random_string()

        ftr = asyncio.get_running_loop().create_future()
        self._pending_futures[response_id] = ftr
        await ws_client.send_json(self.config.bot_id, {"action": action, "params": data, "echo": response_id})
        return await ftr

    def _check_execution(self, data: Any):
        if isinstance(data, dict):
            if data.get("status") == "failed":
                raise ExecutionException("execution failed")
            return data["data"]

    async def ensure_execution(self, relationship: Relationship, execution: Execution) -> Any:
        return await self._ensure_execution(self, relationship=relationship, execution=execution)

    _ensure_execution = OverrideBus(
        proto_ensure_exec_params,
        {"execution": execution_subbus, "network": network_method_subbus},
        {"network": lambda: "http"},
    )

    @_ensure_execution.override(execution=FetchBot, network="http")
    @_ensure_execution.override(execution=FetchBot, network="http-service")
    @_ensure_execution.override(execution=FetchBot, network="ws")
    @_ensure_execution.override(execution=FetchBot, network="ws-service")
    async def get_bot(self, relationship: Relationship, execution: FetchBot) -> "Entity[SelfProfile]":
        return Entity(self.config.bot_id, SelfProfile())

    @_ensure_execution.override(execution=FetchStranger, network="http")
    async def get_stranger_http(
        self, relationship: Relationship, execution: FetchStranger
    ) -> "Entity[StrangerProfile]":
        data = _GetStranger_Resp.parse_obj(
            self._check_execution(await self._http_post("/get_stranger_info", {"user_id": int(execution.target)}))
        )

        return Entity(id=data.user_id, profile=StrangerProfile(data.nickname, data.age))

    @_ensure_execution.override(execution=FetchStranger, network="ws")
    async def get_stranger_ws(self, relationship: Relationship, execution: FetchStranger) -> "Entity[StrangerProfile]":
        data = _GetStranger_Resp.parse_obj(
            self._check_execution(
                await self._ws_client_send_packet("get_stranger_info", {"user_id": int(execution.target)})
            )
        )

        return Entity(id=data.user_id, profile=StrangerProfile(data.nickname, data.age))

    @_ensure_execution.override(execution=FetchFriends, network="http")
    async def get_friends_http(
        self, relationship: Relationship, execution: FetchFriends
    ) -> "Iterable[Entity[FriendProfile]]":
        data = _GetFriends_Resp.parse_obj(self._check_execution(await self._http_get("/get_friends")))

        return [Entity(id=i.user_id, profile=FriendProfile(i.nickname, i.remark)) for i in data.__root__]

    @_ensure_execution.override(execution=FetchFriends, network="ws")
    async def get_friends_ws(
        self, relationship: Relationship, execution: FetchFriends
    ) -> "Iterable[Entity[FriendProfile]]":
        data = _GetFriends_Resp.parse_obj(self._check_execution(await self._ws_client_send_packet("get_friends", {})))

        return [Entity(id=i.user_id, profile=FriendProfile(i.nickname, i.remark)) for i in data.__root__]

    @_ensure_execution.override(execution=FetchGroups, network="http")
    async def get_groups_http(
        self, relationship: Relationship, execution: FetchGroups
    ) -> "Iterable[Group[GroupProfile]]":
        data = _GetGroups_Resp.parse_obj(self._check_execution(await self._http_get("/get_group_list")))

        return [
            Group(id=i.group_id, profile=GroupProfile(i.group_name, i.member_count, i.max_member_count))
            for i in data.__root__
        ]

    @_ensure_execution.override(execution=FetchGroups, network="ws")
    async def get_groups_ws(
        self, relationship: Relationship, execution: FetchGroups
    ) -> "Iterable[Group[GroupProfile]]":
        data = _GetGroups_Resp.parse_obj(self._check_execution(await self._ws_client_send_packet("get_group_list", {})))

        return [Group(id=i.group_id, profile=GroupProfile(i.group_name, i.group_id)) for i in data.__root__]

    @_ensure_execution.override(execution=FetchMembers, network="http")
    async def get_members_http(
        self, relationship: Relationship, execution: FetchMembers
    ) -> "Iterable[Entity[MemberProfile]]":
        data = _GetMembers_Resp.parse_obj(
            self._check_execution(
                await self._http_get(
                    "/get_group_member_list",
                    {"group_id": int(isinstance(execution.target, Group) and execution.target.id or execution.target)},
                )
            )
        )

        return [
            Entity(
                id=i.user_id,
                profile=MemberProfile(
                    name=i.name,
                    role={
                        "owner": Role.Owner,
                        "admin": Role.Admin,
                        "member": Role.Member,
                    }[i.role],
                    nickname=i.nickname,
                    title=i.title,
                ),
            )
            for i in data.__root__
        ]

    @_ensure_execution.override(execution=FetchMembers, network="ws")
    async def get_members_ws(
        self, relationship: Relationship, execution: FetchMembers
    ) -> "Iterable[Entity[MemberProfile]]":
        data = _GetMembers_Resp.parse_obj(
            self._check_execution(
                await self._ws_client_send_packet(
                    "get_group_member_list",
                    {"group_id": int(isinstance(execution.target, Group) and execution.target.id or execution.target)},
                )
            )
        )

        return [
            Entity(
                i.user_id,
                MemberProfile(
                    i.name,
                    {
                        "owner": Role.Owner,
                        "admin": Role.Admin,
                        "member": Role.Member,
                    }[i.role],
                    i.nickname,
                    i.title,
                ),
            )
            for i in data.__root__
        ]

    @_ensure_execution.override(execution=FetchMember, network="http")
    async def get_member_http(self, relationship: Relationship, execution: FetchMember) -> "Entity[MemberProfile]":
        data = _GetMembers_Resp_MemberItem.parse_obj(
            self._check_execution(
                await self._http_post(
                    "/get_group_member_info",
                    {
                        "group_id": int(isinstance(execution.group, Group) and execution.group.id or execution.group),
                        "user_id": int(execution.target),
                    },
                )
            )
        )

        return Entity(data.user_id, MemberProfile(data.name, data.role, data.nickname, data.title))

    @_ensure_execution.override(execution=MemberRemove, network="http")
    async def remove_member_http(self, relationship: Relationship, execution: MemberRemove) -> None:
        self._check_execution(
            await self._http_post(
                "/set_group_kick",
                {
                    "group_id": int(isinstance(execution.group, Group) and execution.group.id or execution.group),
                    "user_id": int(execution.target),
                },
            )
        )

    @_ensure_execution.override(execution=MemberRemove, network="ws")
    async def remove_member_ws(self, relationship: Relationship, execution: MemberRemove) -> None:
        self._check_execution(
            await self._ws_client_send_packet(
                "set_group_kick",
                {
                    "group_id": int(isinstance(execution.group, Group) and execution.group.id or execution.group),
                    "user_id": int(execution.target),
                },
            )
        )

    @_ensure_execution.override(execution=MemberMute, network="http")
    async def mute_http(self, relationship: Relationship, execution: MemberMute) -> None:
        self._check_execution(
            await self._http_post(
                "/set_group_ban",
                {
                    "group_id": int(isinstance(execution.group, Group) and execution.group.id or execution.group),
                    "user_id": int(execution.target),
                    "duration": execution.duration,
                },
            )
        )

    @_ensure_execution.override(execution=MemberMute, network="ws")
    async def mute_ws(self, relationship: Relationship, execution: MemberMute) -> None:
        self._check_execution(
            await self._ws_client_send_packet(
                "set_group_ban",
                {
                    "group_id": int(isinstance(execution.group, Group) and execution.group.id or execution.group),
                    "user_id": int(execution.target),
                    "duration": execution.duration,
                },
            )
        )

    @_ensure_execution.override(execution=MemberUnmute, network="http")
    async def unmute_http(self, relationship: Relationship, execution: MemberUnmute) -> None:
        self._check_execution(
            await self._http_post(
                "/set_group_ban",
                {
                    "group_id": int(isinstance(execution.group, Group) and execution.group.id or execution.group),
                    "user_id": int(execution.target),
                    "duration": 0,
                },
            )
        )

    @_ensure_execution.override(execution=MemberUnmute, network="ws")
    async def unmute_ws(self, relationship: Relationship, execution: MemberUnmute) -> None:
        self._check_execution(
            await self._ws_client_send_packet(
                "set_group_ban",
                {
                    "group_id": int(isinstance(execution.group, Group) and execution.group.id or execution.group),
                    "user_id": int(execution.target),
                    "duration": 0,
                },
            )
        )

    @_ensure_execution.override(execution=GroupMute, network="http")
    async def group_mute_http(self, relationship: Relationship, execution: GroupMute) -> None:
        self._check_execution(
            await self._http_post(
                "/set_group_whole_ban",
                {
                    "group_id": int(isinstance(execution.target, Group) and execution.target.id or execution.target),
                    "enable": True,
                },
            )
        )

    @_ensure_execution.override(execution=GroupMute, network="ws")
    async def group_mute_ws(self, relationship: Relationship, execution: GroupUnmute) -> None:
        self._check_execution(
            await self._ws_client_send_packet(
                "set_group_whole_ban",
                {
                    "group_id": int(isinstance(execution.target, Group) and execution.target.id or execution.target),
                    "enable": True,
                },
            )
        )

    @_ensure_execution.override(execution=GroupUnmute, network="http")
    async def group_unmute_http(self, relationship: Relationship, execution: GroupUnmute) -> None:
        self._check_execution(
            await self._http_post(
                "/set_group_whole_ban",
                {
                    "group_id": int(isinstance(execution.target, Group) and execution.target.id or execution.target),
                    "enable": False,
                },
            )
        )

    @_ensure_execution.override(execution=GroupUnmute, network="ws")
    async def group_unmute_ws(self, relationship: Relationship, execution: GroupUnmute) -> None:
        self._check_execution(
            await self._ws_client_send_packet(
                "set_group_whole_ban",
                {
                    "group_id": int(isinstance(execution.target, Group) and execution.target.id or execution.target),
                    "enable": False,
                },
            )
        )

    @_ensure_execution.override(execution=MemberPromoteToAdministrator, network="http")
    async def promote_to_admin_http(self, relationship: Relationship, execution: MemberPromoteToAdministrator) -> None:
        self._check_execution(
            await self._http_post(
                "/set_group_admin",
                {
                    "group_id": isinstance(execution.group, Group) and execution.group.id or execution.group,
                    "user_id": execution.target,
                    "enable": True,
                },
            )
        )

    @_ensure_execution.override(execution=MemberPromoteToAdministrator, network="ws")
    async def promote_to_admin_ws(self, relationship: Relationship, execution: MemberPromoteToAdministrator) -> None:
        self._check_execution(
            await self._ws_client_send_packet(
                "set_group_admin", {"group_id": execution.group, "user_id": execution.target, "enable": True}
            )
        )

    @_ensure_execution.override(execution=MemberDemoteFromAdministrator, network="http")
    async def demote_from_admin_http(
        self, relationship: Relationship, execution: MemberDemoteFromAdministrator
    ) -> None:
        self._check_execution(
            await self._http_post(
                "/set_group_admin",
                {
                    "group_id": int(isinstance(execution.group, Group) and execution.group.id or execution.group),
                    "user_id": int(execution.target),
                    "enable": False,
                },
            )
        )

    @_ensure_execution.override(execution=MemberDemoteFromAdministrator, network="ws")
    async def demote_from_admin_ws(self, relationship: Relationship, execution: MemberDemoteFromAdministrator) -> None:
        self._check_execution(
            await self._ws_client_send_packet(
                "set_group_admin",
                {
                    "group_id": int(isinstance(execution.group, Group) and execution.group.id or execution.group),
                    "user_id": int(execution.target),
                    "enable": False,
                },
            )
        )

    @_ensure_execution.override(execution=MemberNicknameSet, network="http")
    async def set_nickname_http(self, relationship: Relationship, execution: MemberNicknameSet) -> None:
        self._check_execution(
            await self._http_post(
                "/set_group_card",
                {
                    "group_id": int(isinstance(execution.group, Group) and execution.group.id or execution.group),
                    "user_id": int(execution.target),
                    "card": execution.nickname,
                },
            )
        )

    @_ensure_execution.override(execution=MemberNicknameSet, network="ws")
    async def set_nickname_ws(self, relationship: Relationship, execution: MemberNicknameSet) -> None:
        self._check_execution(
            await self._ws_client_send_packet(
                "set_group_card",
                {
                    "group_id": int(isinstance(execution.group, Group) and execution.group.id or execution.group),
                    "user_id": int(execution.target),
                    "card": execution.nickname,
                },
            )
        )

    @_ensure_execution.override(execution=MemberNicknameClear, network="http")
    async def clear_nickname_http(self, relationship: Relationship, execution: MemberNicknameClear) -> None:
        self._check_execution(
            await self._http_post(
                "/set_group_card",
                {
                    "group_id": int(isinstance(execution.group, Group) and execution.group.id or execution.group),
                    "user_id": int(execution.target),
                    "card": "",
                },
            )
        )

    @_ensure_execution.override(execution=MemberNicknameClear, network="ws")
    async def clear_nickname_ws(self, relationship: Relationship, execution: MemberNicknameClear) -> None:
        self._check_execution(
            await self._ws_client_send_packet(
                "set_group_card",
                {
                    "group_id": int(isinstance(execution.group, Group) and execution.group.id or execution.group),
                    "user_id": int(execution.target),
                    "card": "",
                },
            )
        )

    @_ensure_execution.override(execution=GroupNameSet, network="http")
    async def set_group_name_http(self, relationship: Relationship, execution: GroupNameSet) -> None:
        self._check_execution(
            await self._http_post(
                "/set_group_name",
                {
                    "group_id": int(isinstance(execution.target, Group) and execution.target.id or execution.target),
                    "name": execution.name,
                },
            )
        )

    @_ensure_execution.override(execution=GroupNameSet, network="ws")
    async def set_group_name_ws(self, relationship: Relationship, execution: GroupNameSet) -> None:
        self._check_execution(
            await self._ws_client_send_packet(
                "set_group_name",
                {
                    "group_id": int(isinstance(execution.target, Group) and execution.target.id or execution.target),
                    "name": execution.name,
                },
            )
        )

    @_ensure_execution.override(execution=GroupLeave, network="http")
    async def leave_group_http(self, relationship: Relationship, execution: GroupLeave) -> None:
        self._check_execution(
            await self._http_post(
                "/set_group_leave",
                {
                    "group_id": int(isinstance(execution.target, Group) and execution.target.id or execution.target),
                },
            )
        )

    @_ensure_execution.override(execution=GroupLeave, network="ws")
    async def leave_group_ws(self, relationship: Relationship, execution: GroupLeave) -> None:
        self._check_execution(
            await self._ws_client_send_packet(
                "set_group_leave",
                {"group_id": int(isinstance(execution.target, Group) and execution.target.id or execution.target)},
            )
        )

    @_ensure_execution.override(execution=MemberSpecialTitleSet, network="http")
    async def set_special_title_http(self, relationship: Relationship, execution: MemberSpecialTitleSet) -> None:
        self._check_execution(
            await self._http_post(
                "/set_group_special_title",
                {
                    "group_id": int(isinstance(execution.group, Group) and execution.group.id or execution.group),
                    "user_id": int(isinstance(execution.target, Entity) and execution.target.id or execution.target),
                    "title": execution.title,
                },
            )
        )

    @_ensure_execution.override(execution=MemberSpecialTitleSet, network="ws")
    async def set_special_title_ws(self, relationship: Relationship, execution: MemberSpecialTitleSet) -> None:
        self._check_execution(
            await self._ws_client_send_packet(
                "set_group_special_title",
                {
                    "group_id": int(isinstance(execution.group, Group) and execution.group.id or execution.group),
                    "user_id": int(isinstance(execution.target, Entity) and execution.target.id or execution.target),
                    "title": execution.title,
                },
            )
        )

    @_ensure_execution.override(execution=MessageSend, network="http")
    async def send_message_http(self, relationship: Relationship, execution: MessageSend) -> MessageId:
        if isinstance(relationship.entity_or_group.profile, MemberProfile):
            data = await self._http_post(
                "/send_group_msg",
                {
                    "group_id": int(
                        (
                            isinstance(execution.target.profile, MemberProfile)
                            and execution.target.profile.group.id
                            or isinstance(execution.target, Group)
                            and execution.target.id
                            or execution.target
                        )
                    ),
                    "message": await self.serialize_message(execution.message),
                },
            )
        else:
            data = await self._http_post(
                "/send_private_msg",
                {
                    "user_id": int(
                        (
                            isinstance(execution.target, Entity)
                            and isinstance(execution.target.profile, FriendProfile)
                            and execution.target.id
                            or execution.target
                        )
                    ),
                    "message": await self.serialize_message(execution.message),
                },
            )
        self._check_execution(data)
        return MessageId(id=str(data["data"]["message_id"]))

    @_ensure_execution.override(execution=MessageSend, network="ws")
    async def send_message_ws(self, relationship: Relationship, execution: MessageSend) -> MessageId:
        if isinstance(relationship.entity_or_group.profile, MemberProfile):
            data = await self._ws_client_send_packet(
                "send_group_msg",
                {
                    "group_id": int(
                        (
                            isinstance(execution.target.profile, MemberProfile)
                            and execution.target.profile.group.id
                            or isinstance(execution.target, Group)
                            and execution.target.id
                            or execution.target
                        )
                    ),
                    "message": await self.serialize_message(execution.message),
                },
            )
        else:
            data = await self._ws_client_send_packet(
                "send_private_msg",
                {
                    "user_id": int(
                        (
                            isinstance(execution.target, Entity)
                            and isinstance(execution.target.profile, FriendProfile)
                            and execution.target.id
                            or execution.target
                        )
                    ),
                    "message": await self.serialize_message(execution.message),
                },
            )
        self._check_execution(data)
        return MessageId(id=str(data["data"]["message_id"]))

    @_ensure_execution.override(execution=MessageRevoke, network="http")
    async def revoke_message_http(self, relationship: Relationship, execution: MessageRevoke) -> None:
        self._check_execution(
            await self._http_post(
                "/delete_msg",
                {
                    "message_id": int(execution.target),
                },
            )
        )

    @_ensure_execution.override(execution=MessageRevoke, network="ws")
    async def revoke_message_ws(self, relationship: Relationship, execution: MessageRevoke) -> None:
        self._check_execution(
            await self._ws_client_send_packet(
                "delete_msg",
                {
                    "message_id": int(execution.target),
                },
            )
        )

    @_ensure_execution.override(execution=MessageFetch, network="http")
    async def fetch_message_http(self, relationship: Relationship, execution: MessageFetch) -> MessageFetchResult:
        return MessageFetchResult.parse_obj(
            self._check_execution(
                await self._http_get(
                    "/get_msg",
                    {
                        "message_id": int(execution.target),
                    },
                )
            )
        )

    @_ensure_execution.override(execution=MessageFetch, network="http")
    async def fetch_message_http(self, relationship: Relationship, execution: MessageFetch) -> MessageFetchResult:
        return MessageFetchResult.parse_obj(
            self._check_execution(
                await self._http_get(
                    "/get_msg",
                    {
                        "message_id": int(execution.target),
                    },
                )
            )
        )

    @_ensure_execution.override(execution=MessageSendPrivate, network="ws")
    async def send_private_message_ws(self, relationship: Relationship, execution: MessageSendPrivate) -> None:
        data = await self._ws_client_send_packet(
            "send_private_msg",
            {
                "user_id": int(
                    (isinstance(execution.target, Entity) and isinstance(execution.target.profile, FriendProfile))
                    and execution.target.id
                    or execution.target
                ),
                "message": await self.serialize_message(execution.message),
            },
        )
        self._check_execution(data)
        return MessageId(id=str(data["message_id"]))

    @_ensure_execution.override(execution=MessageSendPrivate, network="http")
    async def send_private_message_http(self, relationship: Relationship, execution: MessageSendPrivate) -> None:
        data = await self._http_post(
            "/send_private_msg",
            {
                "user_id": int(
                    (isinstance(execution.target, Entity) and isinstance(execution.target.profile, FriendProfile))
                    and execution.target.id
                    or execution.target
                ),
                "message": await self.serialize_message(execution.message),
            },
        )
        self._check_execution(data)
        return MessageId(id=str(data["message_id"]))
