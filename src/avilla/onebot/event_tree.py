from typing import Any, Awaitable, Callable, Dict, Tuple, Type

from graia.broadcast.entities.event import Dispatchable
from avilla.event.message import *
from avilla.event.notice import *
from avilla.event.request import *
from avilla.onebot.profile import AnonymousProfile
from avilla.role import Role

if TYPE_CHECKING:
    from avilla.onebot.protocol import OnebotProtocol

ROLE_MAP = {"owner": Role.Owner, "admin": Role.Admin, "member": Role.Member}

# (post_type, sub_type=None, msg_type=None, notice_type=None, request_type=None, meta_event_type=None) => Type[Dispatchable]
EVENT_PARSING_TREE: Dict[
    Tuple[str, str, str, str, str, str], Callable[["OnebotProtocol", Dict[str, Any]], Awaitable[Dispatchable]]
] = {}


def gen_parsing_key(x: Dict):
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
async def _(proto: "OnebotProtocol", x: Dict[str, Any]):
    return MessageEvent(
        entity_or_group=Entity(
            x["user_id"], FriendProfile(name=x["sender"]["nickname"], remark=x["sender"]["nickname"])
        ),
        message=await proto.parse_message(x["message"]),
        message_id=str(x["message_id"]),
        current_id=str(x["self_id"]),
        time=datetime.fromtimestamp(x["time"]),
    )


@register("message", "private", "group")
async def _(proto: "OnebotProtocol", x: Dict[str, Any]):
    return MessageEvent(
        entity_or_group=Entity(
            x["user_id"],
            MemberProfile(
                name=x["sender"]["nickname"],
            ),
        ),
        message=await proto.parse_message(x["message"]),
        message_id=str(x["message_id"]),
        current_id=str(x["self_id"]),
        time=datetime.fromtimestamp(x["time"]),
    )


@register("message", "group", "normal")
async def _(proto: "OnebotProtocol", x: Dict[str, Any]):
    return MessageEvent(
        entity_or_group=Entity(
            x["user_id"],
            MemberProfile(
                name=x["sender"]["nickname"],
                group=Group(x["group_id"], GroupProfile(name=None)),
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
async def _(proto: "OnebotProtocol", x: Dict[str, Any]):
    return MessageEvent(
        entity_or_group=Entity(
            x["user_id"],
            AnonymousProfile(
                id=x["anonymous"]["id"],
                group=Group(x["group_id"], GroupProfile(name=None)),
                name=x["anonymous"]["name"],
                _internal_id=x["anonymous"]["flag"],
            ),
        ),
        message=await proto.parse_message(x["message"]),
        message_id=str(x["message_id"]),
        current_id=str(x["self_id"]),
        time=datetime.fromtimestamp(x["time"]),
    )
