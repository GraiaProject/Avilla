from typing import TYPE_CHECKING, Any, Iterable

from avilla.builtins.profile import (FriendProfile, GroupProfile,
                                     MemberProfile, SelfProfile,
                                     StrangerProfile)
from avilla.entity import Entity
from avilla.exceptions import ExecutionException
from avilla.execution import Execution
from avilla.execution.fetch import (FetchBot, FetchFriend, FetchFriends,
                                    FetchGroup, FetchGroups, FetchMember,
                                    FetchMembers, FetchStranger)
from avilla.execution.group import (GroupLeave, GroupMute, GroupNameSet,
                                    GroupUnmute, MemberDemoteFromAdministrator,
                                    MemberMute, MemberNicknameClear,
                                    MemberNicknameSet,
                                    MemberPromoteToAdministrator, MemberRemove,
                                    MemberSpecialTitleSet, MemberUnmute)
from avilla.execution.message import (MessageFetch, MessageFetchResult,
                                      MessageId, MessageRevoke, MessageSend,
                                      MessageSendPrivate)
from avilla.group import Group, GroupPtr
from avilla.role import Role
from avilla.utilles.override_bus import OverrideBus
from avilla.utilles.override_subbus import (execution_subbus,
                                            network_method_subbus,
                                            proto_ensure_exec_params)

from .resp import (_GetFriends_Resp, _GetFriends_Resp_FriendItem,
                   _GetGroups_Resp, _GetGroups_Resp_GroupItem,
                   _GetMembers_Resp, _GetMembers_Resp_MemberItem,
                   _GetStranger_Resp)

if TYPE_CHECKING:
    from .protocol import OnebotProtocol


ensure_execution: "OverrideBus[OnebotProtocol]" = OverrideBus(
    proto_ensure_exec_params,
    {"execution": execution_subbus, "network": network_method_subbus},
    {"network": lambda: "http"},
)


def _extract_and_check_as_groupid(execution: Execution) -> int:
    if isinstance(execution.target, str):
        if not execution.target.isdigit():
            raise ValueError(f"invalid group id: {execution.target}")
        return int(execution.target)
    elif isinstance(execution.target, int):
        return execution.target
    elif isinstance(execution.target, Entity) and isinstance(
        execution.target.profile, MemberProfile
    ):
        if execution.target.profile.group is None:
            raise ValueError(f"invalid input, maybe you can issue the problem: {execution}")
        if not execution.target.profile.group.id.isdigit():
            raise ValueError(f"invalid group id: {execution.target.profile.group.id}")
        return int(execution.target.profile.group.id)
    elif isinstance(execution.target, Group):
        if not execution.target.id.isdigit():
            raise ValueError(f"invalid group id: {execution.target.__repr__()}")
        return int(execution.target.id)
    else:
        raise ValueError(f"invalid target: {execution.target}")


def _check_execution(data: Any):
    if isinstance(data, dict):
        if data.get("status") == "failed":
            raise ExecutionException("execution failed")
        return data["data"]


@ensure_execution.override(execution=FetchBot, network="http")
@ensure_execution.override(execution=FetchBot, network="http-service")
@ensure_execution.override(execution=FetchBot, network="ws")
@ensure_execution.override(execution=FetchBot, network="ws-service")
async def get_bot(self: "OnebotProtocol", execution: FetchBot) -> "Entity[SelfProfile]":
    return Entity(self.config.bot_id, SelfProfile())


@ensure_execution.override(execution=FetchStranger, network="http")
async def get_stranger_http(self, execution: FetchStranger) -> "Entity[StrangerProfile]":
    data = _GetStranger_Resp.parse_obj(
        _check_execution(
            await self._http_post("/get_stranger_info", {"user_id": int(execution.target)})
        )
    )

    return Entity(id=data.user_id, profile=StrangerProfile(name=data.nickname, age=data.age))


@ensure_execution.override(execution=FetchStranger, network="ws")
async def get_stranger_ws(self, execution: FetchStranger) -> "Entity[StrangerProfile]":
    data = _GetStranger_Resp.parse_obj(
        _check_execution(
            await self._ws_client_send_packet(
                "get_stranger_info", {"user_id": int(execution.target)}
            )
        )
    )

    return Entity(id=data.user_id, profile=StrangerProfile(name=data.nickname, age=data.age))


@ensure_execution.override(execution=FetchFriend, network="http")
async def get_friend_http(self, execution: FetchFriend) -> "Entity[FriendProfile]":
    data = _GetFriends_Resp_FriendItem.parse_obj(
        _check_execution(
            await self._http_post("/get_friend_info", {"user_id": int(execution.target)})
        )
    )

    return Entity(id=data.user_id, profile=FriendProfile(name=data.nickname, remark=data.remark))


@ensure_execution.override(execution=FetchFriend, network="ws")
async def get_friend_ws(self: "OnebotProtocol", execution: FetchFriend) -> "Entity[FriendProfile]":
    data = _GetFriends_Resp_FriendItem.parse_obj(
        _check_execution(
            await self._ws_client_send_packet("get_friend_info", {"user_id": int(execution.target)})
        )
    )

    return Entity(id=data.user_id, profile=FriendProfile(name=data.nickname, remark=data.remark))


@ensure_execution.override(execution=FetchFriends, network="http")
async def get_friends_http(self, execution: FetchFriends) -> "Iterable[Entity[FriendProfile]]":
    data = _GetFriends_Resp.parse_obj(_check_execution(await self._http_get("/get_friends")))

    return [
        Entity(id=i.user_id, profile=FriendProfile(name=i.nickname, remark=i.remark))
        for i in data.__root__
    ]


@ensure_execution.override(execution=FetchFriends, network="ws")
async def get_friends_ws(self, execution: FetchFriends) -> "Iterable[Entity[FriendProfile]]":
    data = _GetFriends_Resp.parse_obj(
        _check_execution(await self._ws_client_send_packet("get_friends", {}))
    )

    return [
        Entity(id=i.user_id, profile=FriendProfile(name=i.nickname, remark=i.remark))
        for i in data.__root__
    ]


@ensure_execution.override(execution=FetchGroup, netwotk="http")
async def get_group_http(self: "OnebotProtocol", execution: FetchGroup) -> "Group":
    group_id = _extract_and_check_as_groupid(execution)

    data = _GetGroups_Resp_GroupItem.parse_obj(
        _check_execution(
            await self._http_post(
                "/get_group_info",
                {"group_id": group_id},
            )
        )
    )

    return Group(
        id=data.group_id,
        profile=GroupProfile(
            name=data.group_name, counts=data.member_count, limit=data.max_member_count
        ),
    )


@ensure_execution.override(execution=FetchGroup, network="ws")
async def get_group_ws(self: "OnebotProtocol", execution: FetchGroup) -> "Group":
    group_id = _extract_and_check_as_groupid(execution)

    data = _GetGroups_Resp_GroupItem.parse_obj(
        _check_execution(
            await self._ws_client_send_packet(
                "get_group_info",
                {"group_id": group_id},
            )
        )
    )

    return Group(
        id=data.group_id,
        profile=GroupProfile(
            name=data.group_name, counts=data.member_count, limit=data.max_member_count
        ),
    )


@ensure_execution.override(execution=FetchGroups, network="http")
async def get_groups_http(self: "OnebotProtocol", execution: FetchGroups) -> "Iterable[Group]":
    data = _GetGroups_Resp.parse_obj(_check_execution(await self._http_get("/get_group_list")))

    return [
        Group(
            id=i.group_id,
            profile=GroupProfile(
                name=i.group_name, counts=i.member_count, limit=i.max_member_count
            ),
        )
        for i in data.__root__
    ]


@ensure_execution.override(execution=FetchGroups, network="ws")
async def get_groups_ws(self: "OnebotProtocol", execution: FetchGroups) -> "Iterable[Group]":
    data = _GetGroups_Resp.parse_obj(
        _check_execution(await self._ws_client_send_packet("get_group_list", {}))
    )

    return [Group(id=i.group_id, profile=GroupProfile(name=i.group_name)) for i in data.__root__]


@ensure_execution.override(execution=FetchMembers, network="http")
async def get_members_http(self, execution: FetchMembers) -> "Iterable[Entity[MemberProfile]]":
    group_id = _extract_and_check_as_groupid(execution)

    data = _GetMembers_Resp.parse_obj(
        _check_execution(
            await self._http_get(
                "/get_group_member_list",
                {"group_id": str(group_id)},
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
                group=Group(str(group_id), GroupProfile()),
            ),
        )
        for i in data.__root__
    ]


@ensure_execution.override(execution=FetchMembers, network="ws")
async def get_members_ws(self, execution: FetchMembers) -> "Iterable[Entity[MemberProfile]]":
    group_id = _extract_and_check_as_groupid(execution)

    data = _GetMembers_Resp.parse_obj(
        _check_execution(
            await self._ws_client_send_packet(
                "get_group_member_list",
                {"group_id": group_id},
            )
        )
    )

    return [
        Entity(
            i.user_id,
            MemberProfile(
                name=i.name,
                group=Group(str(group_id), GroupProfile()),
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


@ensure_execution.override(execution=FetchMember, network="http")
async def get_member_http(self, execution: FetchMember) -> "Entity[MemberProfile]":
    group_id = execution.target

    data = _GetMembers_Resp_MemberItem.parse_obj(
        _check_execution(
            await self._http_post(
                "/get_group_member_info",
                {
                    "group_id": group_id,
                    "user_id": int(execution.target),
                },
            )
        )
    )

    return Entity(
        data.user_id,
        MemberProfile(
            name=data.name,
            group=Group(str(group_id), GroupProfile()),
            role=data.role,
            nickname=data.nickname,
            title=data.title,
        ),
    )


@ensure_execution.override(execution=MemberRemove, network="http")
async def remove_member_http(self: "OnebotProtocol", execution: MemberRemove) -> None:
    group_id = _extract_and_check_as_groupid(execution)

    _check_execution(
        await self._http_post(
            "/set_group_kick",
            {
                "group_id": group_id,
                "user_id": int(execution.target),
            },
        )
    )


@ensure_execution.override(execution=MemberRemove, network="ws")
async def remove_member_ws(self: "OnebotProtocol", execution: MemberRemove) -> None:
    group_id = _extract_and_check_as_groupid(execution)

    _check_execution(
        await self._ws_client_send_packet(
            "set_group_kick",
            {
                "group_id": group_id,
                "user_id": int(execution.target),
            },
        )
    )


@ensure_execution.override(execution=MemberMute, network="http")
async def mute_http(self: "OnebotProtocol", execution: MemberMute) -> None:
    group_id = _extract_and_check_as_groupid(execution)

    _check_execution(
        await self._http_post(
            "/set_group_ban",
            {
                "group_id": group_id,
                "user_id": int(execution.target),
                "duration": execution.duration,
            },
        )
    )


@ensure_execution.override(execution=MemberMute, network="ws")
async def mute_ws(self: "OnebotProtocol", execution: MemberMute) -> None:
    group_id = _extract_and_check_as_groupid(execution)

    _check_execution(
        await self._ws_client_send_packet(
            "set_group_ban",
            {
                "group_id": group_id,
                "user_id": int(execution.target),
                "duration": execution.duration,
            },
        )
    )


@ensure_execution.override(execution=MemberUnmute, network="http")
async def unmute_http(self: "OnebotProtocol", execution: MemberUnmute) -> None:
    group_id = _extract_and_check_as_groupid(execution)

    _check_execution(
        await self._http_post(
            "/set_group_ban",
            {
                "group_id": group_id,
                "user_id": int(execution.target),
                "duration": 0,
            },
        )
    )


@ensure_execution.override(execution=MemberUnmute, network="ws")
async def unmute_ws(self: "OnebotProtocol", execution: MemberUnmute) -> None:
    group_id = _extract_and_check_as_groupid(execution)

    _check_execution(
        await self._ws_client_send_packet(
            "set_group_ban",
            {
                "group_id": group_id,
                "user_id": int(execution.target),
                "duration": 0,
            },
        )
    )


@ensure_execution.override(execution=GroupMute, network="http")
async def group_mute_http(self: "OnebotProtocol", execution: GroupMute) -> None:
    group_id = _extract_and_check_as_groupid(execution)

    _check_execution(
        await self._http_post(
            "/set_group_whole_ban",
            {
                "group_id": group_id,
                "enable": True,
            },
        )
    )


@ensure_execution.override(execution=GroupMute, network="ws")
async def group_mute_ws(self: "OnebotProtocol", execution: GroupUnmute) -> None:
    group_id = _extract_and_check_as_groupid(execution)

    _check_execution(
        await self._ws_client_send_packet(
            "set_group_whole_ban",
            {
                "group_id": group_id,
                "enable": True,
            },
        )
    )


@ensure_execution.override(execution=GroupUnmute, network="http")
async def group_unmute_http(self: "OnebotProtocol", execution: GroupUnmute) -> None:
    group_id = _extract_and_check_as_groupid(execution)

    _check_execution(
        await self._http_post(
            "/set_group_whole_ban",
            {
                "group_id": group_id,
                "enable": False,
            },
        )
    )


@ensure_execution.override(execution=GroupUnmute, network="ws")
async def group_unmute_ws(self: "OnebotProtocol", execution: GroupUnmute) -> None:
    group_id = _extract_and_check_as_groupid(execution)

    _check_execution(
        await self._ws_client_send_packet(
            "set_group_whole_ban",
            {
                "group_id": group_id,
                "enable": False,
            },
        )
    )


@ensure_execution.override(execution=MemberPromoteToAdministrator, network="http")
async def promote_to_admin_http(self, execution: MemberPromoteToAdministrator) -> None:
    _check_execution(
        await self._http_post(
            "/set_group_admin",
            {
                "group_id": isinstance(execution.group, Group)
                and execution.group.id
                or execution.group,
                "user_id": execution.target,
                "enable": True,
            },
        )
    )


@ensure_execution.override(execution=MemberPromoteToAdministrator, network="ws")
async def promote_to_admin_ws(self, execution: MemberPromoteToAdministrator) -> None:
    _check_execution(
        await self._ws_client_send_packet(
            "set_group_admin",
            {"group_id": execution.group, "user_id": execution.target, "enable": True},
        )
    )


@ensure_execution.override(execution=MemberDemoteFromAdministrator, network="http")
async def demote_from_admin_http(self, execution: MemberDemoteFromAdministrator) -> None:
    group_id = _extract_and_check_as_groupid(execution)

    _check_execution(
        await self._http_post(
            "/set_group_admin",
            {
                "group_id": group_id,
                "user_id": int(execution.target),
                "enable": False,
            },
        )
    )


@ensure_execution.override(execution=MemberDemoteFromAdministrator, network="ws")
async def demote_from_admin_ws(self, execution: MemberDemoteFromAdministrator) -> None:
    group_id = _extract_and_check_as_groupid(execution)

    _check_execution(
        await self._ws_client_send_packet(
            "set_group_admin",
            {
                "group_id": group_id,
                "user_id": int(execution.target),
                "enable": False,
            },
        )
    )


@ensure_execution.override(execution=MemberNicknameSet, network="http")
async def set_nickname_http(self: "OnebotProtocol", execution: MemberNicknameSet) -> None:
    group_id = _extract_and_check_as_groupid(execution)

    _check_execution(
        await self._http_post(
            "/set_group_card",
            {
                "group_id": group_id,
                "user_id": int(execution.target),
                "card": execution.nickname,
            },
        )
    )


@ensure_execution.override(execution=MemberNicknameSet, network="ws")
async def set_nickname_ws(self: "OnebotProtocol", execution: MemberNicknameSet) -> None:
    group_id = _extract_and_check_as_groupid(execution)

    _check_execution(
        await self._ws_client_send_packet(
            "set_group_card",
            {
                "group_id": group_id,
                "user_id": int(execution.target),
                "card": execution.nickname,
            },
        )
    )


@ensure_execution.override(execution=MemberNicknameClear, network="http")
async def clear_nickname_http(self: "OnebotProtocol", execution: MemberNicknameClear) -> None:
    group_id = _extract_and_check_as_groupid(execution)

    _check_execution(
        await self._http_post(
            "/set_group_card",
            {
                "group_id": group_id,
                "user_id": int(execution.target),
                "card": "",
            },
        )
    )


@ensure_execution.override(execution=MemberNicknameClear, network="ws")
async def clear_nickname_ws(self: "OnebotProtocol", execution: MemberNicknameClear) -> None:
    group_id = _extract_and_check_as_groupid(execution)

    _check_execution(
        await self._ws_client_send_packet(
            "set_group_card",
            {
                "group_id": group_id,
                "user_id": int(execution.target),
                "card": "",
            },
        )
    )


@ensure_execution.override(execution=GroupNameSet, network="http")
async def set_group_name_http(self: "OnebotProtocol", execution: GroupNameSet) -> None:
    group_id = _extract_and_check_as_groupid(execution)

    _check_execution(
        await self._http_post(
            "/set_group_name",
            {
                "group_id": group_id,
                "name": execution.name,
            },
        )
    )


@ensure_execution.override(execution=GroupNameSet, network="ws")
async def set_group_name_ws(self: "OnebotProtocol", execution: GroupNameSet) -> None:
    group_id = _extract_and_check_as_groupid(execution)

    _check_execution(
        await self._ws_client_send_packet(
            "set_group_name",
            {
                "group_id": group_id,
                "name": execution.name,
            },
        )
    )


@ensure_execution.override(execution=GroupLeave, network="http")
async def leave_group_http(self: "OnebotProtocol", execution: GroupLeave) -> None:
    group_id = _extract_and_check_as_groupid(execution)

    _check_execution(
        await self._http_post(
            "/set_group_leave",
            {
                "group_id": group_id,
            },
        )
    )


@ensure_execution.override(execution=GroupLeave, network="ws")
async def leave_group_ws(self: "OnebotProtocol", execution: GroupLeave) -> None:
    group_id = _extract_and_check_as_groupid(execution)

    _check_execution(
        await self._ws_client_send_packet(
            "set_group_leave",
            {
                "group_id": group_id,
            },
        )
    )


@ensure_execution.override(execution=MemberSpecialTitleSet, network="http")
async def set_special_title_http(self: "OnebotProtocol", execution: MemberSpecialTitleSet) -> None:
    group_id = _extract_and_check_as_groupid(execution)
    if isinstance(execution.target, Group):
        target_id = int(execution.target.id)
    elif isinstance(execution.target, str) and execution.target.isdigit():
        target_id = int(execution.target)
    else:
        raise ValueError("target as a target_id, must be digit")

    _check_execution(
        await self._http_post(
            "/set_group_special_title",
            {
                "group_id": group_id,
                "user_id": target_id,
                "title": execution.title,
            },
        )
    )


@ensure_execution.override(execution=MemberSpecialTitleSet, network="ws")
async def set_special_title_ws(self: "OnebotProtocol", execution: MemberSpecialTitleSet) -> None:
    group_id = _extract_and_check_as_groupid(execution)
    if isinstance(execution.target, Group):
        target_id = int(execution.target.id)
    elif isinstance(execution.target, str) and execution.target.isdigit():
        target_id = int(execution.target)
    else:
        raise ValueError("target as a target_id, must be digit")

    _check_execution(
        await self._ws_client_send_packet(
            "set_group_special_title",
            {
                "group_id": group_id,
                "user_id": target_id,
                "title": execution.title,
            },
        )
    )


@ensure_execution.override(execution=MessageSend, network="http")
@ensure_execution.override(execution=MessageSend, network="ws")
async def send_message(self: "OnebotProtocol", execution: MessageSend) -> MessageId:
    using_method = None
    group_id = None
    friend_id = None

    if isinstance(execution.target, str):
        raise ValueError("target as a target_id, must be a Group/GroupPtr or Entity/EntityPtr")

    if isinstance(execution.target, (Group, GroupPtr)):
        group_id = int(execution.target.id)
        using_method = "send_group_msg"
    elif isinstance(execution.target, Entity):
        if isinstance(execution.target.profile, MemberProfile):
            if getattr(execution.target.profile, "group", None) is None:
                raise ValueError("target.profile.group is null")
            group_id = int(execution.target.profile.group.id)  # type: ignore
            using_method = "send_group_msg"
        elif isinstance(execution.target.profile, FriendProfile):
            friend_id = int(execution.target.id)
            using_method = "send_private_msg"
        else:
            raise ValueError(f"unsupported profile type: {type(execution.target.profile)}")
    else:
        raise ValueError(f"unsupported target: {type(execution.target)}")

    data = await self._onebot_send_packet(
        using_method,
        {
            **({"group_id": group_id} if group_id is not None else {}),
            **({"user_id": friend_id} if friend_id is not None else {}),
            "message": [
                *(await self.serialize_message(execution.message)),
                *(
                    [
                        {
                            "type": "reply",
                            "data": {
                                "id": execution.reply.id
                                if isinstance(execution.reply, MessageId)
                                else execution.reply
                            },
                        }
                    ]
                    if execution.reply
                    else []
                ),
            ],
        },
    )

    _check_execution(data)
    return MessageId(id=str(data["data"]["message_id"]))


@ensure_execution.override(execution=MessageRevoke, network="http")
async def revoke_message_http(self: "OnebotProtocol", execution: MessageRevoke) -> None:
    _check_execution(
        await self._http_post(
            "/delete_msg",
            {
                "message_id": int(
                    isinstance(execution.target, MessageId)
                    and execution.target.id
                    or execution.target
                ),
            },
        )
    )


@ensure_execution.override(execution=MessageRevoke, network="ws")
async def revoke_message_ws(self: "OnebotProtocol", execution: MessageRevoke) -> None:
    _check_execution(
        await self._ws_client_send_packet(
            "delete_msg",
            {
                "message_id": int(execution.target),
            },
        )
    )


@ensure_execution.override(execution=MessageFetch, network="http")
async def fetch_message_http(self: "OnebotProtocol", execution: MessageFetch) -> MessageFetchResult:
    return MessageFetchResult.parse_obj(
        _check_execution(
            await self._http_get(
                "/get_msg",
                {
                    "message_id": str(
                        execution.target.id
                        if isinstance(execution.target, MessageId)
                        else execution.target
                    )
                },
            )
        )
    )


@ensure_execution.override(execution=MessageFetch, network="ws")
async def fetch_message_ws(self: "OnebotProtocol", execution: MessageFetch) -> MessageFetchResult:
    return MessageFetchResult.parse_obj(
        _check_execution(
            await self._ws_client_send_packet(
                "get_msg",
                {
                    "message_id": str(
                        execution.target.id
                        if isinstance(execution.target, MessageId)
                        else execution.target
                    )
                },
            )
        )
    )


@ensure_execution.override(execution=MessageSendPrivate, network="ws")
async def send_private_message_ws(self, execution: MessageSendPrivate) -> MessageId:
    if isinstance(execution.target, str):
        if execution.target.isdigit():
            target_id = int(execution.target)
        else:
            raise ValueError("target as a str, must be digit")

    else:
        if hasattr(execution.target, "profile"):
            if isinstance(execution.target, Entity) and isinstance(
                execution.target.profile, FriendProfile
            ):
                target_id = int(execution.target.id)
            else:
                raise ValueError("unsupported entity with profile, it need to be a `friend`.")
        else:
            raise ValueError("unsupported target without profile and not a str")

    data = await self._ws_client_send_packet(
        "send_private_msg",
        {
            "user_id": target_id,
            "message": [
                *(await self.serialize_message(execution.message)),
                *(
                    [
                        {
                            "type": "reply",
                            "data": {
                                "id": execution.reply.id
                                if isinstance(execution.reply, MessageId)
                                else execution.reply
                            },
                        }
                    ]
                    if execution.reply
                    else []
                ),
            ],
        },
    )

    _check_execution(data)

    return MessageId(id=str(data["message_id"]))


@ensure_execution.override(execution=MessageSendPrivate, network="http")
async def send_private_message_http(self, execution: MessageSendPrivate) -> MessageId:
    if isinstance(execution.target, str):
        if execution.target.isdigit():
            target_id = int(execution.target)
        else:
            raise ValueError("target as a str, must be digit")
    else:
        if hasattr(execution.target, "profile"):
            if isinstance(execution.target, Entity) and isinstance(
                execution.target.profile, FriendProfile
            ):
                target_id = int(execution.target.id)
            else:
                raise ValueError("unsupported entity with profile, it need to be a `friend`.")
        else:
            raise ValueError("unsupported target without profile and not a str")

    data = await self._http_post(
        "/send_private_msg",
        {
            "user_id": target_id,
            "message": [
                *(await self.serialize_message(execution.message)),
                *(
                    [
                        {
                            "type": "reply",
                            "data": {
                                "id": execution.reply.id
                                if isinstance(execution.reply, MessageId)
                                else execution.reply
                            },
                        }
                    ]
                    if execution.reply
                    else []
                ),
            ],
        },
    )

    _check_execution(data)

    return MessageId(id=str(data["message_id"]))
