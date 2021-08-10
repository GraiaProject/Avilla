from typing import (TYPE_CHECKING, Any, Awaitable, Callable, Dict, Optional,
                    Tuple)

from graia.broadcast.entities.event import Dispatchable

from avilla.event.notice import (FileInfo, FriendAdd, FriendRevoke,
                                 GroupFileUploadNotice, GroupRevoke,
                                 MemberDemotedFromAdministrator,
                                 MemberJoinedByApprove, MemberJoinedByInvite,
                                 MemberLeave, MemberMuted,
                                 MemberPromotedToAdministrator, MemberRemoved,
                                 MemberUnmuted)
from avilla.event.request import FriendAddRequest, GroupJoinRequest
from avilla.event.service import (NetworkConnected, ServiceOffline,
                                  ServiceOnline)
from avilla.execution.fetch import (FetchFriend, FetchGroup, FetchMember,
                                    FetchStranger)
from avilla.onebot.event import HeartbeatReceived, NudgeEvent

"""
from avilla.event.message import *
from avilla.event.notice import *
from avilla.event.request import *
"""
from datetime import datetime, timedelta

from avilla.builtins.profile import FriendProfile, GroupProfile, MemberProfile
from avilla.entity import Entity
from avilla.event.message import MessageEvent
from avilla.group import Group
from avilla.onebot.profile import AnonymousProfile
from avilla.role import Role

if TYPE_CHECKING:
    from avilla.onebot.protocol import OnebotProtocol

ROLE_MAP = {"owner": Role.Owner, "admin": Role.Admin, "member": Role.Member}

# (post_type, sub_type=None, msg_type=None, notice_type=None, request_type=None, meta_event_type=None)\
#  => Type[Dispatchable]
EVENT_PARSING_TREE: Dict[
    Tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], Optional[str]],
    Callable[["OnebotProtocol", Dict[str, Any]], Awaitable[Dispatchable]],
] = {}


def gen_parsing_key(data: Dict[str, str]):
    return (
        data.get("post_type"),
        data.get("sub_type"),
        data.get("message_type"),
        data.get("notice_type"),
        data.get("request_type"),
        data.get("meta_event_type"),
    )


def register(post, msg=None, sub=None, notice_type=None, request_type=None, meta_event_type=None):
    def wrapper(func: Callable[["OnebotProtocol", Dict[str, Any]], Awaitable[Dispatchable]]):
        EVENT_PARSING_TREE[(post, sub, msg, notice_type, request_type, meta_event_type)] = func
        return func

    return wrapper


@register("message", "private", "friend")
async def message_private_friend(proto: "OnebotProtocol", data: Dict[str, Any]):
    return MessageEvent(
        ctx=Entity(
            data["user_id"],
            FriendProfile(name=data["sender"]["nickname"], remark=data["sender"]["nickname"]),
        ),
        message=await proto.parse_message(data["message"]),
        message_id=str(data["message_id"]),
        current_id=str(data["self_id"]),
        time=datetime.fromtimestamp(data["time"]),
    )


@register("message", "private", "group")
async def message_private_group(proto: "OnebotProtocol", data: Dict[str, Any]):
    return MessageEvent(
        ctx=Entity(
            data["user_id"],
            await proto.ensure_execution(FetchMember(data["group_id"], data["user_id"])),
        ),
        message=await proto.parse_message(data["message"]),
        message_id=str(data["message_id"]),
        current_id=str(data["self_id"]),
        time=datetime.fromtimestamp(data["time"]),
    )


@register("message", "group", "normal")
async def message_group_normal(proto: "OnebotProtocol", data: Dict[str, Any]):
    return MessageEvent(
        ctx=Entity(
            data["user_id"],
            MemberProfile(
                name=data["sender"]["nickname"],
                group=await proto.ensure_execution(FetchGroup(data["group_id"])),
                nickname=data["sender"]["card"],
                role=ROLE_MAP[data["sender"]["role"]],
                title=data["sender"]["title"],
            ),
        ),
        message=await proto.parse_message(data["message"]),
        message_id=str(data["message_id"]),
        current_id=str(data["self_id"]),
        time=datetime.fromtimestamp(data["time"]),
    )


@register("message", "group", "anonymous")
async def message_group_anonymous(proto: "OnebotProtocol", data: Dict[str, Any]):
    return MessageEvent(
        ctx=Entity(
            data["user_id"],
            AnonymousProfile(
                id=data["anonymous"]["id"],
                group=await proto.ensure_execution(FetchGroup(data["group_id"])),
                name=data["anonymous"]["name"],
                _internal_id=data["anonymous"]["flag"],
            ),
        ),
        message=await proto.parse_message(data["message"]),
        message_id=str(data["message_id"]),
        current_id=str(data["self_id"]),
        time=datetime.fromtimestamp(data["time"]),
    )


@register(post="notice", notice_type="group_upload")
async def notice_group_upload(proto: "OnebotProtocol", data: Dict[str, Any]):
    return GroupFileUploadNotice(
        ctx=await proto.ensure_execution(FetchMember(str(data["group_id"]), data["user_id"])),
        file=FileInfo(data["file"]["id"], data["file"]["name"], data["file"]["size"]),
        current_id=str(data["self_id"]),
        time=datetime.fromtimestamp(data["time"]),
    )


@register(post="notice", notice_type="group_admin", sub="set")
async def notice_group_admin_set(protocol: "OnebotProtocol", data: Dict):
    return MemberPromotedToAdministrator(
        ctx=await protocol.ensure_execution(FetchMember(str(data["group_id"]), data["user_id"])),
        group=await protocol.ensure_execution(FetchGroup(str(data["group_id"]))),
        current_id=str(data["self_id"]),
        time=datetime.fromtimestamp(data["time"]),
    )


@register(post="notice", notice_type="group_admin", sub="unset")
async def notice_group_admin_unset(protocol: "OnebotProtocol", data: Dict):
    return MemberDemotedFromAdministrator(
        ctx=await protocol.ensure_execution(FetchMember(str(data["group_id"]), data["user_id"])),
        group=await protocol.ensure_execution(FetchGroup(str(data["group_id"]))),
        current_id=str(data["self_id"]),
        time=datetime.fromtimestamp(data["time"]),
    )


@register(post="notice", notice_type="group_decrease", sub="leave")
async def notice_group_decrease_leave(protocol: "OnebotProtocol", data: Dict):
    return MemberLeave(
        ctx=Entity(
            id=str(data["user_id"]),
            profile=await protocol.ensure_execution(FetchGroup(str(data["group_id"]))),
        ),
        group=await protocol.ensure_execution(FetchGroup(str(data["group_id"]))),
        current_id=str(data["self_id"]),
        time=datetime.fromtimestamp(data["time"]),
    )


@register(post="notice", notice_type="group_decrease", sub="kick")
async def notice_group_decrease_kick(protocol: "OnebotProtocol", data: Dict):
    return MemberRemoved(
        ctx=Entity(
            id=str(data["user_id"]),
            profile=await protocol.ensure_execution(FetchGroup(str(data["group_id"]))),
        ),
        group=await protocol.ensure_execution(FetchGroup(str(data["group_id"]))),
        current_id=str(data["self_id"]),
        time=datetime.fromtimestamp(data["time"]),
    )


@register(post="notice", notice_type="group_decrease", sub="kick_me")
async def notice_group_decrease_kick_me(protocol: "OnebotProtocol", data: Dict):
    g = Group(id=data["group_id"], profile=GroupProfile())
    return MemberRemoved(
        ctx=protocol.get_self(),
        group=g,
        current_id=str(data["self_id"]),
        time=datetime.fromtimestamp(data["time"]),
    )


@register(post="notice", notice_type="group_increase", sub="approve")
async def notice_group_increase_approve(protocol: "OnebotProtocol", data: Dict):
    return MemberJoinedByApprove(
        ctx=await protocol.ensure_execution(FetchMember(str(data["group_id"]), data["user_id"])),
        group=await protocol.ensure_execution(FetchGroup(str(data["group_id"]))),
        operator=await protocol.ensure_execution(
            FetchMember(str(data["group_id"]), data["operator_id"])
        ),
        current_id=str(data["self_id"]),
        time=datetime.fromtimestamp(data["time"]),
    )


@register(post="notice", notice_type="group_increase", sub="invite")
async def notice_group_increase_invite(protocol: "OnebotProtocol", data: Dict):
    return MemberJoinedByInvite(
        ctx=await protocol.ensure_execution(FetchMember(str(data["group_id"]), data["user_id"])),
        group=await protocol.ensure_execution(FetchGroup(str(data["group_id"]))),
        operator=await protocol.ensure_execution(
            FetchMember(str(data["group_id"]), data["operator_id"])
        ),
        current_id=str(data["self_id"]),
        time=datetime.fromtimestamp(data["time"]),
    )


@register(post="notice", notice_type="group_ban", sub="ban")
async def notice_group_ban(protocol: "OnebotProtocol", data: Dict):
    return MemberMuted(
        ctx=await protocol.ensure_execution(FetchMember(str(data["group_id"]), data["user_id"])),
        group=await protocol.ensure_execution(FetchGroup(str(data["group_id"]))),
        operator=await protocol.ensure_execution(
            FetchMember(str(data["group_id"]), data["operator_id"])
        ),
        duration=timedelta(seconds=data["duration"]),
        current_id=str(data["self_id"]),
        time=datetime.fromtimestamp(data["time"]),
    )


@register(post="notice", notice_type="group_ban", sub="lift_ban")
async def notice_group_ban_lift(protocol: "OnebotProtocol", data: Dict):
    return MemberUnmuted(
        ctx=await protocol.ensure_execution(FetchMember(str(data["group_id"]), data["user_id"])),
        group=await protocol.ensure_execution(FetchGroup(str(data["group_id"]))),
        operator=await protocol.ensure_execution(
            FetchMember(str(data["group_id"]), data["operator_id"])
        ),
        current_id=str(data["self_id"]),
        time=datetime.fromtimestamp(data["time"]),
    )


@register(post="notice", notice_type="friend_add")
async def notice_friend_add(protocol: "OnebotProtocol", data: Dict):
    return FriendAdd(
        ctx=await protocol.ensure_execution(FetchFriend(str(data["user_id"]))),
        current_id=str(data["self_id"]),
        time=datetime.fromtimestamp(data["time"]),
    )


@register(post="notice", notice_type="group_recall")
async def notice_group_recall(protocol: "OnebotProtocol", data: Dict):
    return GroupRevoke(
        ctx=await protocol.ensure_execution(
            FetchMember(str(data["group_id"]), str(data["user_id"]))
        ),
        group=await protocol.ensure_execution(FetchGroup(str(data["group_id"]))),
        operator=await protocol.ensure_execution(
            FetchMember(str(data["group_id"]), data["operator_id"])
        ),
        message_id=str(data["message_id"]),
        current_id=str(data["self_id"]),
        time=datetime.fromtimestamp(data["time"]),
    )


@register(post="notice", notice_type="friend_recall")
async def notice_friend_recall(protocol: "OnebotProtocol", data: Dict):
    return FriendRevoke(
        ctx=await protocol.ensure_execution(FetchFriend(data["user_id"])),
        message_id=str(data["message_id"]),
        current_id=str(data["self_id"]),
        time=datetime.fromtimestamp(data["time"]),
    )


@register(post="request", request_type="friend")
async def request_friend(protocol: "OnebotProtocol", data: Dict):
    return FriendAddRequest(
        ctx=await protocol.ensure_execution(FetchStranger(str(data["user_id"]))),
        comment=data["comment"],
        request_id=data["flag"],
        current_id=str(data["self_id"]),
        time=datetime.fromtimestamp(data["time"]),
    )


@register(post="request", request_type="group", sub="add")
async def request_group_add(protocol: "OnebotProtocol", data: Dict):
    return GroupJoinRequest(
        ctx=await protocol.ensure_execution(FetchStranger(str(data["user_id"]))),
        request_type="common",
        comment=data["comment"],
        request_id=data["flag"],
        group=await protocol.ensure_execution(FetchGroup(str(data["group_id"]))),
        current_id=str(data["self_id"]),
        time=datetime.fromtimestamp(data["time"]),
    )


@register(post="request", request_type="group", sub="invite")
async def request_group_invite(protocol: "OnebotProtocol", data: Dict):
    return GroupJoinRequest(
        ctx=await protocol.ensure_execution(FetchStranger(str(data["user_id"]))),
        request_type="invite",
        comment=data["comment"],
        request_id=data["flag"],
        group=await protocol.ensure_execution(FetchGroup(str(data["group_id"]))),
        current_id=str(data["self_id"]),
        time=datetime.fromtimestamp(data["time"]),
    )


@register(post="meta_event", meta_event_type="lifecycle", sub="enable")
async def meta_event_lifecycle_enable(protocol: "OnebotProtocol", data: Dict):
    return ServiceOnline()


@register(post="meta_event", meta_event_type="lifecycle", sub="disable")
async def meta_event_lifecycle_disable(protocol: "OnebotProtocol", data: Dict):
    return ServiceOffline()


@register(post="meta_event", meta_event_type="lifecycle", sub="connect")
async def meta_event_lifecycle_connect(protocol: "OnebotProtocol", data: Dict):
    return NetworkConnected()


@register(post="meta_event", meta_event_type="heartbeat")
async def meta_event_heartbeat(protocol: "OnebotProtocol", data: Dict):
    return HeartbeatReceived(data["status"], data["interval"])


@register(post="notice", notice_type="notify", sub="poke")
async def notice_notify_poke(protocol: "OnebotProtocol", data: Dict):
    return NudgeEvent(
        ctx=await protocol.ensure_execution(
            FetchMember(str(data["group_id"]), str(data["target_id"]))
        ),
        group=await protocol.ensure_execution(FetchGroup(str(data["group_id"]))),
        operator=await protocol.ensure_execution(
            FetchMember(str(data["group_id"]), data["user_id"])
        ),
        current_id=str(data["self_id"]),
        time=datetime.fromtimestamp(data["time"]),
    )
