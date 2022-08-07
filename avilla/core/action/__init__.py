from __future__ import annotations

import inspect
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar

from graia.amnesia.message import Element, MessageChain

from avilla.core.action.extension import ActionExtension
from avilla.core.context import ctx_relationship
from avilla.core.elements import Text
from avilla.core.message import Message
from avilla.core.request import Request
from avilla.core.typing import ActionExtensionImpl
from avilla.core.utilles.selector import Selector

if TYPE_CHECKING:
    from avilla.core.relationship import Relationship, RelationshipExecutor


class Action:
    def set_target(self, target: Selector):
        ...

    def set_default_target(self, relationship: Relationship) -> Selector | None:
        ...


_Ext = TypeVar("_Ext", bound=ActionExtension)


def extension(extension_type: type[_Ext]):
    def wrapper(func: ActionExtensionImpl):
        func.__implemented_extension__ = extension_type
        return func

    return wrapper


class StandardActionImpl:
    actions: ClassVar[list[type[Action]]] = []
    endpoint: ClassVar[str]
    extension_impls: dict[type[ActionExtension], ActionExtensionImpl] = {}

    def __init_subclass__(cls) -> None:
        cls.extension_impls = {}
        for parent in reversed(cls.__mro__):
            if issubclass(parent, StandardActionImpl):
                cls.extension_impls.update(parent.extension_impls)
        for _, value in inspect.getmembers(cls):
            ext_type = getattr(value, "__implemented_extension__", None)
            if ext_type is not None:
                cls.extension_impls[ext_type] = value

    @classmethod
    def is_implemented(cls, extension_type: type[ActionExtension]) -> bool:
        return extension_type in cls.extension_impls

    @staticmethod
    async def get_execute_params(executor: RelationshipExecutor) -> dict[str, Any] | None:
        ...

    @staticmethod
    def unwarp_result(executor: RelationshipExecutor, result: Any) -> Any:
        return result


R = TypeVar("R")


class Result(Generic[R]):
    pass


class MessageSend(Result[Selector], Action):
    target: Selector
    message: MessageChain
    reply: Selector | None = None

    def __init__(
        self,
        message: MessageChain | str | Iterable[str | Element],
        *,
        reply: Message | Selector | str | None = None,
    ):
        if isinstance(message, str):
            message = MessageChain([Text(message)])
        elif not isinstance(message, MessageChain):
            message = MessageChain([]).extend(list(message))
        self.message = message

        if isinstance(reply, Message):
            reply = reply.to_selector()
        elif isinstance(reply, str):
            rs = ctx_relationship.get(None)
            self.reply = rs.mainline.copy().message(reply) if rs else Selector().message(reply)

    def set_target(self, target: Selector):
        self.target = target

    def set_default_target(self, relationship: Relationship):
        self.target = relationship.mainline
        return relationship.mainline


class MessageRevoke(Action):
    message: Selector

    def __init__(self, message: Selector):
        self.message = message


class MessageEdit(Action):
    message: Selector
    to: MessageChain

    def __init__(self, message: Selector, to: MessageChain):
        self.message = message
        self.to = to


class MessageFetch(Result[Message], Action):
    message: Selector

    def __init__(self, message: Selector):
        self.message = message


class RequestAction(Result[None], Action):
    request: Selector

    def __init__(self, request: Request | Selector):
        if isinstance(request, Request):
            request = request.to_selector()
        self.request = request


class RequestAccept(RequestAction):
    pass


class RequestReject(RequestAction):
    pass


class RequestCancel(RequestAction):
    pass


class RequestIgnore(RequestAction):
    pass


class RelationshipDestroy(Action):
    pass


# TODO: 成员操作, 对 mainline(场景) 内的成员的相关操作.


class MemberRemove(Action):
    member: Selector

    def __init__(self, member: Selector):
        self.member = member
