from typing import Optional, TYPE_CHECKING, Any, Awaitable, Callable, Dict, Tuple

from graia.broadcast.entities.event import Dispatchable

from avilla.event.notice import (
    FileInfo,
    FriendAdd,
    FriendRevoke,
    GroupFileUploadNotice,
    GroupRevoke,
    MemberDemotedFromAdministrator,
    MemberJoinedByApprove,
    MemberJoinedByInvite,
    MemberLeave,
    MemberMuted,
    MemberPromotedToAdministrator,
    MemberRemoved,
    MemberUnmuted,
)
from avilla.event.request import FriendAddRequest, GroupJoinRequest
from avilla.event.service import NetworkConnected, ServiceOffline, ServiceOnline
from avilla.execution.fetch import FetchFriend, FetchGroup, FetchMember, FetchStranger
from avilla.onebot.event import HeartbeatReceived

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


def gen_parsing_key(x: Dict[str, str]):
    return (
        x.get("post_type"),
        x.get("message_type"),
        x.get("sub_type"),
        x.get("notice_type"),
        x.get("request_type"),
        x.get("meta_event_type"),
    )


def register(post, sub=None, msg=None, notice_type=None, request_type=None, meta_event_type=None):
    def wrapper(func: Callable[["OnebotProtocol", Dict[str, Any]], Awaitable[Dispatchable]]):
        EVENT_PARSING_TREE[(post, sub, msg, notice_type, request_type, meta_event_type)] = func
        return func

    return wrapper


@register("message", "private", "friend")
async def message_private_friend(proto: "OnebotProtocol", x: Dict[str, Any]):
    return MessageEvent(
        entity_or_group=Entity(
            x["user_id"],
            FriendProfile(name=x["sender"]["nickname"], remark=x["sender"]["nickname"]),
        ),
        message=await proto.parse_message(x["message"]),
        message_id=str(x["message_id"]),
        current_id=str(x["self_id"]),
        time=datetime.fromtimestamp(x["time"]),
    )


@register("message", "private", "group")
async def message_private_group(proto: "OnebotProtocol", x: Dict[str, Any]):
    return MessageEvent(
        entity_or_group=Entity(
            x["user_id"],
            await proto.ensure_execution(None, FetchMember(x['group_id'], x['user_id'])), # type: ignore
        ),
        message=await proto.parse_message(x["message"]),
        message_id=str(x["message_id"]),
        current_id=str(x["self_id"]),
        time=datetime.fromtimestamp(x["time"]),
    )


@register("message", "group", "normal")
async def message_group_normal(proto: "OnebotProtocol", x: Dict[str, Any]):
    return MessageEvent(
        entity_or_group=Entity(
            x["user_id"],
            MemberProfile(
                name=x["sender"]["nickname"],
                group=await proto.ensure_execution(None, FetchGroup(x['group_id'])), # type: ignore
                nickname=x["sender"]["card"],
                role=ROLE_MAP[x["sender"]["role"]],
                title=x["sender"]["title"],
            ),
        ),
        message=await proto.parse_message(x["message"]),
        message_id=str(x["message_id"]),
        current_id=str(x["self_id"]),
        time=datetime.fromtimestamp(x["time"]),
    )


@register("message", "group", "anonymous")
async def message_group_anonymous(proto: "OnebotProtocol", x: Dict[str, Any]):
    return MessageEvent(
        entity_or_group=Entity(
            x["user_id"],
            AnonymousProfile(
                id=x["anonymous"]["id"],
                group=await proto.ensure_execution(None, FetchGroup(x['group_id'])), # type: ignore
                name=x["anonymous"]["name"],
                _internal_id=x["anonymous"]["flag"],
            ),
        ),
        message=await proto.parse_message(x["message"]),
        message_id=str(x["message_id"]),
        current_id=str(x["self_id"]),
        time=datetime.fromtimestamp(x["time"]),
    )


@register(post="notice", notice_type="group_upload")
async def notice_group_upload(proto: "OnebotProtocol", x: Dict[str, Any]):
    return GroupFileUploadNotice(
        entity_or_group=await proto.ensure_execution(
            None, FetchMember(str(x["group_id"]), x["user_id"])  # type: ignore
        ),
        file=FileInfo(x["file"]["id"], x["file"]["name"], x["file"]["size"]),
        current_id=str(x["self_id"]),
        time=datetime.fromtimestamp(x["time"]),
    )


@register(post="notice", notice_type="group_admin", sub="set")
async def notice_group_admin_set(p: "OnebotProtocol", x: Dict):
    return MemberPromotedToAdministrator(
        entity_or_group=await p.ensure_execution(
            None, FetchMember(str(x["group_id"]), x["user_id"])  # type: ignore
        ),
        group=await p.ensure_execution(None, FetchGroup(str(x["group_id"]))),  # type: ignore
        current_id=str(x["self_id"]),
        time=datetime.fromtimestamp(x["time"]),
    )


@register(post="notice", notice_type="group_admin", sub="unset")
async def notice_group_admin_unset(p: "OnebotProtocol", x: Dict):
    return MemberDemotedFromAdministrator(
        entity_or_group=await p.ensure_execution(
            None, FetchMember(str(x["group_id"]), x["user_id"])  # type: ignore
        ),
        group=await p.ensure_execution(None, FetchGroup(str(x["group_id"]))),  # type: ignore
        current_id=str(x["self_id"]),
        time=datetime.fromtimestamp(x["time"]),
    )


@register(post="notice", notice_type="group_decrease", sub="leave")
async def notice_group_decrease_leave(p: "OnebotProtocol", x: Dict):
    return MemberLeave(
        entity_or_group=Entity(
            id=str(x["user_id"]),
            profile=await p.ensure_execution(None, FetchGroup(str(x["group_id"]))),  # type: ignore
        ),
        group=await p.ensure_execution(None, FetchGroup(str(x["group_id"]))),  # type: ignore
        current_id=str(x["self_id"]),
        time=datetime.fromtimestamp(x["time"]),
    )


@register(post="notice", notice_type="group_decrease", sub="kick")
async def notice_group_decrease_kick(p: "OnebotProtocol", x: Dict):
    return MemberRemoved(
        entity_or_group=Entity(
            id=str(x["user_id"]),
            profile=await p.ensure_execution(None, FetchGroup(str(x["group_id"]))),  # type: ignore
        ),
        group=await p.ensure_execution(None, FetchGroup(str(x["group_id"]))),  # type: ignore
        current_id=str(x["self_id"]),
        time=datetime.fromtimestamp(x["time"]),
    )


@register(post="notice", notice_type="group_decrease", sub="kick_me")
async def notice_group_decrease_kick_me(p: "OnebotProtocol", x: Dict):
    g = Group(id=x["group_id"], profile=GroupProfile())
    return MemberRemoved(
        entity_or_group=p.get_self(),
        group=g,
        current_id=str(x["self_id"]),
        time=datetime.fromtimestamp(x["time"]),
    )


@register(post="notice", notice_type="group_increase", sub="approve")
async def notice_group_increase_approve(p: "OnebotProtocol", x: Dict):
    return MemberJoinedByApprove(
        entity_or_group=await p.ensure_execution(
            None, FetchMember(str(x["group_id"]), x["user_id"])  # type: ignore
        ),
        group=await p.ensure_execution(None, FetchGroup(str(x["group_id"]))),  # type: ignore
        operator=await p.ensure_execution(
            None, FetchMember(str(x["group_id"]), x["operator_id"])  # type: ignore
        ),
        current_id=str(x["self_id"]),
        time=datetime.fromtimestamp(x["time"]),
    )


@register(post="notice", notice_type="group_increase", sub="invite")
async def notice_group_increase_invite(p: "OnebotProtocol", x: Dict):
    return MemberJoinedByInvite(
        entity_or_group=await p.ensure_execution(
            None, FetchMember(str(x["group_id"]), x["user_id"])  # type: ignore
        ),
        group=await p.ensure_execution(None, FetchGroup(str(x["group_id"]))),  # type: ignore
        operator=await p.ensure_execution(
            None, FetchMember(str(x["group_id"]), x["operator_id"])  # type: ignore
        ),
        current_id=str(x["self_id"]),
        time=datetime.fromtimestamp(x["time"]),
    )


@register(post="notice", notice_type="group_ban", sub="ban")
async def notice_group_ban(p: "OnebotProtocol", x: Dict):
    return MemberMuted(
        entity_or_group=await p.ensure_execution(
            None, FetchMember(str(x["group_id"]), x["user_id"])  # type: ignore
        ),
        group=await p.ensure_execution(None, FetchGroup(str(x["group_id"]))),  # type: ignore
        operator=await p.ensure_execution(
            None, FetchMember(str(x["group_id"]), x["operator_id"])  # type: ignore
        ),
        duration=timedelta(seconds=x["duration"]),
        current_id=str(x["self_id"]),
        time=datetime.fromtimestamp(x["time"]),
    )


# TODO: 自动获取 Member Profile, 对, 就这上面几个 notice event


@register(post="notice", notice_type="group_ban", sub="lift_ban")
async def notice_group_ban_lift(p: "OnebotProtocol", x: Dict):
    return MemberUnmuted(
        entity_or_group=await p.ensure_execution(
            None, FetchMember(str(x["group_id"]), x["user_id"])  # type: ignore
        ),
        group=await p.ensure_execution(None, FetchGroup(str(x["group_id"]))),  # type: ignore
        operator=await p.ensure_execution(
            None, FetchMember(str(x["group_id"]), x["operator_id"])  # type: ignore
        ),
        current_id=str(x["self_id"]),
        time=datetime.fromtimestamp(x["time"]),
    )


@register(post="notice", notice_type="friend_add")
async def notice_friend_add(p: "OnebotProtocol", x: Dict):
    return FriendAdd(
        entity_or_group=await p.ensure_execution(
            None, FetchFriend(str(x["user_id"]))  # type: ignore
        ),
        current_id=str(x["self_id"]),
        time=datetime.fromtimestamp(x["time"]),
    )


@register(post="notice", notice_type="group_recall")
async def notice_group_recall(p: "OnebotProtocol", x: Dict):
    return GroupRevoke(
        entity_or_group=await p.ensure_execution(
            None, FetchMember(str(x["group_id"]), str(x["user_id"]))  # type: ignore
        ),
        group=await p.ensure_execution(None, FetchGroup(str(x["group_id"]))),  # type: ignore
        operator=await p.ensure_execution(
            None, FetchMember(str(x["group_id"]), x["operator_id"])  # type: ignore
        ),
        message_id=str(x["message_id"]),
        current_id=str(x["self_id"]),
        time=datetime.fromtimestamp(x["time"]),
    )


@register(post="notice", notice_type="friend_recall")
async def notice_friend_recall(p: "OnebotProtocol", x: Dict):
    return FriendRevoke(
        entity_or_group=await p.ensure_execution(None, FetchFriend()),  # type: ignore
        message_id=str(x["message_id"]),
        current_id=str(x["self_id"]),
        time=datetime.fromtimestamp(x["time"]),
    )


@register(post="request", request_type="friend")
async def request_friend(p: "OnebotProtocol", x: Dict):
    return FriendAddRequest(
        entity_or_group=await p.ensure_execution(
            None, FetchStranger(str(x["user_id"]))  # type: ignore
        ),
        comment=x["comment"],
        request_id=x["flag"],
        current_id=str(x["self_id"]),
        time=datetime.fromtimestamp(x["time"]),
    )


@register(post="request", request_type="group", sub="add")
async def request_group_add(p: "OnebotProtocol", x: Dict):
    return GroupJoinRequest(
        entity_or_group=await p.ensure_execution(
            None, FetchStranger(str(x["user_id"]))  # type: ignore
        ),
        request_type="common",
        comment=x["comment"],
        request_id=x["flag"],
        group=await p.ensure_execution(None, FetchGroup(str(x["group_id"]))),  # type: ignore
        current_id=str(x["self_id"]),
        time=datetime.fromtimestamp(x["time"]),
    )


@register(post="request", request_type="group", sub="invite")
async def request_group_invite(p: "OnebotProtocol", x: Dict):
    return GroupJoinRequest(
        entity_or_group=await p.ensure_execution(None, FetchStranger(str(x["user_id"]))),  # type: ignore
        request_type="invite",
        comment=x["comment"],
        request_id=x["flag"],
        group=await p.ensure_execution(None, FetchGroup(str(x["group_id"]))),  # type: ignore
        current_id=str(x["self_id"]),
        time=datetime.fromtimestamp(x["time"]),
    )


@register(post="meta_event", meta_event_type="lifecycle", sub="enable")
async def meta_event_lifecycle_enable(p: "OnebotProtocol", x: Dict):
    return ServiceOnline()


@register(post="meta_event", meta_event_type="lifecycle", sub="disable")
async def meta_event_lifecycle_disable(p: "OnebotProtocol", x: Dict):
    return ServiceOffline()


@register(post="meta_event", meta_event_type="lifecycle", sub="connect")
async def meta_event_lifecycle_connect(p: "OnebotProtocol", x: Dict):
    return NetworkConnected()


@register(post="meta_event", meta_event_type="heartbeat")
async def meta_event_heartbeat(p: "OnebotProtocol", x: Dict):
    return HeartbeatReceived(x["status"], x["interval"])
