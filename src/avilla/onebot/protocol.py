import asyncio
import json
from typing import AsyncIterable, Dict, List, Tuple, Type, Union

from pydantic.main import BaseModel

from avilla import Avilla
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
from avilla.relationship import Relationship
from avilla.utilles import random_string
from avilla.utilles.transformer import JsonTransformer, Utf8StringTransformer
from avilla.utilles.override_bus import OverrideBus
from avilla.utilles.override_subbus import proto_ensure_exec_params, network_method_subbus, execution_subbus

from .resp import *


class OnebotProtocol(BaseProtocol):
    config: OnebotConfig

    _pending_futures: Dict[str, asyncio.Future]

    def __post_init__(self) -> None:
        self._pending_futures = {}

        if self.using_exec_method is WebsocketCommunication:
            ws_client: AbstractWebsocketClient = self.avilla.network_interface.get_network("ws")

            @ws_client.on_received_data(self.config.bot_id)
            def onebot_ws_data_received(client, connid, raw_data: Union[str, bytes]):
                if isinstance(raw_data, bytes):
                    raw_data = raw_data.decode()
                data: Dict = json.loads(raw_data)
                is_event = "post_type" in data
                if is_event:
                    pass  # TODO: Event Parse.
                else:
                    p_ftr = self._pending_futures.get(data["echo"])
                    if p_ftr:
                        p_ftr.set_result(data)

    def ensureNetworks(
        self, avilla: "Avilla"
    ) -> Tuple[
        Dict[str, Union[Client, Service]], Union[Type[ClientCommunicationMethod], Type[ServiceCommunicationMethod]]
    ]:
        result = {}
        comm_method = None
        if "http" in self.config.communications:
            result["http"] = avilla.network_interface.get_network("http")
            comm_method = HttpCommunication
        if "ws" in self.config.communications:
            result["ws"] = avilla.network_interface.get_network("ws")
            comm_method = WebsocketCommunication
        if result:
            return result, comm_method

        if "http-service" in self.config.communications:
            result["http-service"] = avilla.network_interface.get_network("http-service")
        if "ws-service" in self.config.communications:
            result["ws-service"] = avilla.network_interface.get_network("ws-service")
            comm_method = ReverseWebsocketCommunication

        if result and comm_method:
            return result, comm_method
        else:
            raise TypeError("invaild config for network")

    def getSelf(self) -> "Entity[SelfProfile]":
        return Entity(self.config.bot_id, SelfProfile())

    async def getMembers(
        self, group: Group[GroupProfile]
    ) -> "AsyncIterable[Entity[Union[SelfProfile, MemberProfile]]]":
        ...  # TODO

    async def parseMessage(self, data: List) -> "MessageChain":
        ...  # TODO

    async def serializeMessage(self, message: "MessageChain") -> List:
        ...  # TODO

    async def getRelationship(
        self, entity: "Entity[Union[MemberProfile, FriendProfile]]"
    ) -> "Relationship[Union[MemberProfile, FriendProfile], GroupProfile, OnebotProtocol]":
        ...  # TODO

    async def launchEntry(self):
        ...  # TODO

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
        await ws_client.send_text(
            self.config.bot_id, json.dumps({"action": action, "params": data, "echo": response_id})
        )
        return await ftr

    async def _check_execution(self, data: Any):
        if isinstance(data, dict):
            if data["status"] == "failed":
                raise ExecutionException("execution failed")
            return data["data"]

    ensureExecution = OverrideBus(
        proto_ensure_exec_params,
        {"execution": execution_subbus, "network": network_method_subbus},
        {"network": lambda: "http"},
    )

    @ensureExecution.override(execution=FetchBot, network="http")
    @ensureExecution.override(execution=FetchBot, network="http-service")
    @ensureExecution.override(execution=FetchBot, network="ws")
    @ensureExecution.override(execution=FetchBot, network="ws-service")
    async def getBot(self, rs: Relationship, exec: FetchBot) -> "Entity[SelfProfile]":
        return Entity(self.config.bot_id, SelfProfile())

    @ensureExecution.override(execution=FetchStranger, network="http")
    async def getStrangerHttp(self, rs: Relationship, exec: FetchStranger) -> "Entity[StrangerProfile]":
        data = _GetStranger_Resp.parse_obj(
            self._check_execution(await self._http_post("/get_stranger_info", {"user_id": exec.target}))
        )

        return Entity(id=data.user_id, profile=StrangerProfile(data.nickname, data.age))

    @ensureExecution.override(execution=FetchStranger, network="ws")
    async def getStrangerWs(self, rs: Relationship, exec: FetchStranger) -> "Entity[StrangerProfile]":
        data = _GetStranger_Resp.parse_obj(
            self._check_execution(await self._ws_client_send_packet("get_stranger_info", {"user_id": exec.target}))
        )

        return Entity(id=data.user_id, profile=StrangerProfile(data.nickname, data.age))

    @ensureExecution.override(execution=FetchFriends, network="http")
    async def getFriendsHttp(self, rs: Relationship, exec: FetchFriends) -> "Iterable[Entity[FriendProfile]]":
        data = _GetFriends_Resp.parse_obj(self._check_execution(await self._http_get("/get_friends")))

        return [Entity(id=i.user_id, profile=FriendProfile(i.nickname, i.remark)) for i in data.__root__]

    @ensureExecution.override(execution=FetchFriends, network="ws")
    async def getFriendsWs(self, rs: Relationship, exec: FetchFriends) -> "Iterable[Entity[FriendProfile]]":
        data = _GetFriends_Resp.parse_obj(self._check_execution(await self._ws_client_send_packet("get_friends", {})))

        return [Entity(id=i.user_id, profile=FriendProfile(i.nickname, i.remark)) for i in data.__root__]

    @ensureExecution.override(execution=FetchGroups, network="http")
    async def getGroupsHttp(self, rs: Relationship, exec: FetchGroups) -> "Iterable[Group[GroupProfile]]":
        data = _GetGroups_Resp.parse_obj(self._check_execution(await self._http_get("/get_group_list")))

        return [
            Group(id=i.group_id, profile=GroupProfile(i.group_name, i.member_count, i.max_member_count))
            for i in data.__root__
        ]

    @ensureExecution.override(execution=FetchGroups, network="ws")
    async def getGroupsWs(self, rs: Relationship, exec: FetchGroups) -> "Iterable[Group[GroupProfile]]":
        data = _GetGroups_Resp.parse_obj(self._check_execution(await self._ws_client_send_packet("get_group_list", {})))

        return [Group(id=i.group_id, profile=GroupProfile(i.group_name, i.group_id)) for i in data.__root__]

    @ensureExecution.override(execution=FetchMembers, network="http")
    async def getMembersHttp(self, rs: Relationship, exec: FetchMembers) -> "Iterable[Entity[MemberProfile]]":
        data = _GetMembers_Resp.parse_obj(
            self._check_execution(
                await self._http_get(
                    "/get_group_member_list",
                    {"group_id": isinstance(exec.target, Group) and exec.target.id or exec.target},
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

    @ensureExecution.override(execution=FetchMembers, network="ws")
    async def getMembersWs(self, rs: Relationship, exec: FetchMembers) -> "Iterable[Entity[MemberProfile]]":
        data = _GetMembers_Resp.parse_obj(
            self._check_execution(await self._ws_client_send_packet("get_group_member_list", {"group_id": exec.group}))
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

    @ensureExecution.override(execution=FetchMember, network="http")
    async def getMemberHttp(self, rs: Relationship, exec: FetchMember) -> "Entity[MemberProfile]":
        data = _GetMembers_Resp_MemberItem.parse_obj(
            self._check_execution(
                await self._http_post(
                    "/get_group_member_info",
                    {
                        "group_id": isinstance(exec.group, Group) and exec.group.id or exec.group,
                        "user_id": exec.target,
                    },
                )
            )
        )

        return Entity(data.user_id, MemberProfile(data.name, data.role, data.nickname, data.title))

    @ensureExecution.override(execution=MemberRemove, network="http")
    async def removeMemberHTTP(self, rs: Relationship, exec: MemberRemove) -> None:
        await self._http_post(
            "/set_group_kick",
            {
                "group_id": isinstance(exec.group, Group) and exec.group.id or exec.group,
                "user_id": exec.target,
            },
        )

    @ensureExecution.override(execution=MemberRemove, network="ws")
    async def removeMemberWs(self, rs: Relationship, exec: MemberRemove) -> None:
        await self._ws_client_send_packet("set_group_kick", {"group_id": exec.group, "user_id": exec.target})

    @ensureExecution.override(execution=MemberMute, network="http")
    async def mute_http(self, rs: Relationship, exec: MemberMute) -> None:
        await self._http_post(
            "/set_group_ban",
            {
                "group_id": isinstance(exec.group, Group) and exec.group.id or exec.group,
                "user_id": exec.target,
                "duration": exec.duration,
            },
        )

    @ensureExecution.override(execution=MemberMute, network="ws")
    async def mute_ws(self, rs: Relationship, exec: MemberMute) -> None:
        await self._ws_client_send_packet(
            "set_group_ban", {"group_id": exec.group, "user_id": exec.target, "duration": exec.duration}
        )

    @ensureExecution.override(execution=MemberUnmute, network="http")
    async def unmute_http(self, rs: Relationship, exec: MemberUnmute) -> None:
        await self._http_post(
            "/set_group_ban",
            {
                "group_id": isinstance(exec.group, Group) and exec.group.id or exec.group,
                "user_id": exec.target,
                "duration": 0,
            },
        )

    @ensureExecution.override(execution=MemberUnmute, network="ws")
    async def unmute_ws(self, rs: Relationship, exec: MemberUnmute) -> None:
        await self._ws_client_send_packet(
            "set_group_ban", {"group_id": exec.group, "user_id": exec.target, "duration": 0}
        )

    @ensureExecution.override(execution=GroupMute, network="http")
    async def group_mute_http(self, rs: Relationship, exec: GroupMute) -> None:
        await self._http_post(
            "/set_group_whole_ban",
            {
                "group_id": isinstance(exec.group, Group) and exec.group.id or exec.group,
                "enable": True,
            },
        )

    @ensureExecution.override(execution=GroupMute, network="ws")
    async def group_mute_ws(self, rs: Relationship, exec: GroupUnmute) -> None:
        await self._ws_client_send_packet("set_group_whole_ban", {"group_id": exec.group, "enable": True})

    @ensureExecution.override(execution=GroupUnmute, network="http")
    async def group_unmute_http(self, rs: Relationship, exec: GroupUnmute) -> None:
        await self._http_post(
            "/set_group_whole_ban",
            {
                "group_id": isinstance(exec.group, Group) and exec.group.id or exec.group,
                "enable": False,
            },
        )

    @ensureExecution.override(execution=GroupUnmute, network="ws")
    async def group_unmute_ws(self, rs: Relationship, exec: GroupUnmute) -> None:
        await self._ws_client_send_packet("set_group_whole_ban", {"group_id": exec.group, "enable": False})

    @ensureExecution.override(execution=MemberPromoteToAdministrator, network="http")
    async def promote_to_admin_http(self, rs: Relationship, exec: MemberPromoteToAdministrator) -> None:
        await self._http_post(
            "/set_group_admin",
            {
                "group_id": isinstance(exec.group, Group) and exec.group.id or exec.group,
                "user_id": exec.target,
                "enable": True,
            },
        )

    @ensureExecution.override(execution=MemberPromoteToAdministrator, network="ws")
    async def promote_to_admin_ws(self, rs: Relationship, exec: MemberPromoteToAdministrator) -> None:
        await self._ws_client_send_packet(
            "set_group_admin", {"group_id": exec.group, "user_id": exec.target, "enable": True}
        )

    @ensureExecution.override(execution=MemberDemoteFromAdministrator, network="http")
    async def demote_from_admin_http(self, rs: Relationship, exec: MemberDemoteFromAdministrator) -> None:
        await self._http_post(
            "/set_group_admin",
            {
                "group_id": isinstance(exec.group, Group) and exec.group.id or exec.group,
                "user_id": exec.target,
                "enable": False,
            },
        )

    @ensureExecution.override(execution=MemberDemoteFromAdministrator, network="ws")
    async def demote_from_admin_ws(self, rs: Relationship, exec: MemberDemoteFromAdministrator) -> None:
        await self._ws_client_send_packet(
            "set_group_admin", {"group_id": exec.group, "user_id": exec.target, "enable": False}
        )

    @ensureExecution.override(execution=MemberNicknameSet, network="http")
    async def set_nickname_http(self, rs: Relationship, exec: MemberNicknameSet) -> None:
        await self._http_post(
            "/set_group_card",
            {
                "group_id": isinstance(exec.group, Group) and exec.group.id or exec.group,
                "user_id": exec.target,
                "card": exec.nickname,
            },
        )

    @ensureExecution.override(execution=MemberNicknameSet, network="ws")
    async def set_nickname_ws(self, rs: Relationship, exec: MemberNicknameSet) -> None:
        await self._ws_client_send_packet(
            "set_group_card", {"group_id": exec.group, "user_id": exec.target, "card": exec.nickname}
        )

    @ensureExecution.override(execution=MemberNicknameClear, network="http")
    async def clear_nickname_http(self, rs: Relationship, exec: MemberNicknameClear) -> None:
        await self._http_post(
            "/set_group_card",
            {
                "group_id": isinstance(exec.group, Group) and exec.group.id or exec.group,
                "user_id": exec.target,
                "card": "",
            },
        )

    @ensureExecution.override(execution=MemberNicknameClear, network="ws")
    async def clear_nickname_ws(self, rs: Relationship, exec: MemberNicknameClear) -> None:
        await self._ws_client_send_packet(
            "set_group_card", {"group_id": exec.group, "user_id": exec.target, "card": ""}
        )

    @ensureExecution.override(execution=GroupNameSet, network="http")
    async def set_group_name_http(self, rs: Relationship, exec: GroupNameSet) -> None:
        await self._http_post(
            "/set_group_name",
            {
                "group_id": isinstance(exec.group, Group) and exec.group.id or exec.group,
                "name": exec.name,
            },
        )

    @ensureExecution.override(execution=GroupNameSet, network="ws")
    async def set_group_name_ws(self, rs: Relationship, exec: GroupNameSet) -> None:
        await self._ws_client_send_packet("set_group_name", {"group_id": exec.group, "name": exec.name})

    @ensureExecution.override(execution=GroupLeave, network="http")
    async def leave_group_http(self, rs: Relationship, exec: GroupLeave) -> None:
        await self._http_post(
            "/set_group_leave",
            {
                "group_id": isinstance(exec.group, Group) and exec.group.id or exec.group,
                "user_id": exec.target,
            },
        )

    @ensureExecution.override(execution=GroupLeave, network="ws")
    async def leave_group_ws(self, rs: Relationship, exec: GroupLeave) -> None:
        await self._ws_client_send_packet("set_group_leave", {"group_id": exec.group, "user_id": exec.target})

    @ensureExecution.override(execution=MemberSpecialTitleSet, network="http")
    async def set_special_title_http(self, rs: Relationship, exec: MemberSpecialTitleSet) -> None:
        await self._http_post(
            "/set_group_special_title",
            {
                "group_id": isinstance(exec.group, Group) and exec.group.id or exec.group,
                "user_id": exec.target,
                "title": exec.title,
            },
        )

    @ensureExecution.override(execution=MemberSpecialTitleSet, network="ws")
    async def set_special_title_ws(self, rs: Relationship, exec: MemberSpecialTitleSet) -> None:
        await self._ws_client_send_packet(
            "set_group_special_title",
            {
                "group_id": exec.group,
                "user_id": exec.target,
                "title": exec.title,
            },
        )

    @ensureExecution.override(execution=MessageSend, network="http")
    async def send_message_http(self, rs: Relationship, exec: MessageSend) -> MessageId:
        if isinstance(rs.entity_or_group, Group):
            data = await self._http_post(
                "/send_group_message",
                {
                    "group_id": exec.target or rs.entity_or_group.id,
                    "message": await self.serializeMessage(exec.message),
                },
            )
        else:
            data = await self._http_post(
                "/send_private_msg",
                {
                    "user_id": exec.target or rs.entity_or_group.id,
                    "message": await self.serializeMessage(exec.message),
                },
            )
        return MessageId(id=data["message_id"])

    @ensureExecution.override(execution=MessageSend, network="ws")
    async def send_message_ws(self, rs: Relationship, exec: MessageSend) -> MessageId:
        if isinstance(rs.entity_or_group, Group):
            data = await self._ws_client_send_packet(
                "send_group_message",
                {
                    "group_id": exec.target or rs.entity_or_group.id,
                    "message": await self.serializeMessage(exec.message),
                },
            )
        else:
            data = await self._ws_client_send_packet(
                "send_private_msg",
                {
                    "user_id": exec.target or rs.entity_or_group.id,
                    "message": await self.serializeMessage(exec.message),
                },
            )
        return MessageId(id=data["message_id"])

    @ensureExecution.override(execution=MessageRevoke, network="http")
    async def revoke_message_http(self, rs: Relationship, exec: MessageRevoke) -> None:
        await self._http_post(
            "/delete_msg ",
            {
                "message_id": exec.message_id,
            },
        )

    @ensureExecution.override(execution=MessageRevoke, network="ws")
    async def revoke_message_ws(self, rs: Relationship, exec: MessageRevoke) -> None:
        await self._ws_client_send_packet(
            "delete_msg",
            {
                "message_id": exec.message_id,
            },
        )

    @ensureExecution.override(execution=MessageFetch, network="http")
    async def fetch_message_http(self, rs: Relationship, exec: MessageFetch) -> MessageFetchResult:
        return MessageFetchResult.parse_obj(
            await self._http_get(
                "/get_msg",
                {
                    "message_id": exec.message_id,
                },
            )
        )

    @ensureExecution.override(execution=MessageFetch, network="http")
    async def fetch_message_http(self, rs: Relationship, exec: MessageFetch) -> MessageFetchResult:
        return MessageFetchResult.parse_obj(
            await self._http_get(
                "/get_msg",
                {
                    "message_id": exec.message_id,
                },
            )
        )

    @ensureExecution.override(execution=MessageSendPrivate, network="ws")
    async def send_private_message_ws(self, rs: Relationship, exec: MessageSendPrivate) -> None:
        data = await self._ws_client_send_packet(
            "send_private_msg",
            {
                "user_id": exec.target,
                "message": await self.serializeMessage(exec.message),
            },
        )
        return MessageId(id=data["message_id"])

    @ensureExecution.override(execution=MessageSendPrivate, network="http")
    async def send_private_message_http(self, rs: Relationship, exec: MessageSendPrivate) -> None:
        data = await self._http_post(
            "/send_private_msg",
            {
                "user_id": exec.target,
                "message": await self.serializeMessage(exec.message),
            },
        )
        return MessageId(id=data["message_id"])
