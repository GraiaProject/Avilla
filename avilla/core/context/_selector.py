from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Awaitable, Callable, TypeVar, overload

from typing_extensions import Concatenate, ParamSpec, Self, Unpack

from avilla.core.message import Message
from avilla.core.metadata import Metadata, MetadataRoute
from avilla.core.ryanvk.descriptor.base import Fn
from avilla.core.selector import EMPTY_MAP, Selector
from avilla.standard.core.message import MessageSend
from avilla.standard.core.relation import SceneCapability
from avilla.standard.core.request import RequestCapability
from graia.amnesia.message import Element, MessageChain, Text

if TYPE_CHECKING:
    from . import Context

R = TypeVar("R", covariant=True)
P = ParamSpec("P")
_MetadataT = TypeVar("_MetadataT", bound=Metadata)


class ContextSelector(Selector):
    context: Context

    def __init__(self, cx: Context, pattern: Mapping[str, str] = EMPTY_MAP) -> None:
        super().__init__(pattern)
        self.context = cx

    @classmethod
    def from_selector(cls, cx: Context, selector: Selector) -> Self:
        return cls(cx, selector.pattern)

    def pull(
        self, metadata: type[_MetadataT] | MetadataRoute[Unpack[tuple[Any, ...]], _MetadataT]
    ) -> Awaitable[_MetadataT]:
        return self.context.pull(metadata, self)

    @overload
    def __getitem__(self, item: str) -> str:
        ...

    @overload
    def __getitem__(self, item: Fn[Callable[Concatenate[Selector, P], Awaitable[R]]]) -> Callable[P, Awaitable[R]]:
        ...

    def __getitem__(
        self,
        item: str | Fn[Callable[Concatenate[Selector, P], Awaitable[R]]],
    ) -> str | Callable[P, Awaitable[R]]:
        if isinstance(item, str):
            return super().__getitem__(item)

        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return await self.context.staff.call_fn(item, self, *args, **kwargs)

        return wrapper


class ContextClientSelector(ContextSelector):
    ...


class ContextEndpointSelector(ContextSelector):
    def expects_request(self) -> ContextRequestSelector:
        if "request" in self.pattern:
            return ContextRequestSelector.from_selector(self.context, self)

        raise ValueError(f"endpoint {self!r} is not a request endpoint")


class ContextSceneSelector(ContextSelector):
    def leave_scene(self):
        return self.context[SceneCapability.leave](self)

    def disband_scene(self):
        return self.context[SceneCapability.disband](self)

    def send_message(
        self,
        message: MessageChain | Iterable[str | Element] | Element | str,
        *,
        reply: Message | Selector | str | None = None,
    ):
        if isinstance(message, str):
            message = MessageChain([Text(message)])
        elif isinstance(message, Element):
            message = MessageChain([message])
        elif not isinstance(message, MessageChain):
            message = MessageChain([]).extend(list(message))
        else:
            message = MessageChain([i if isinstance(i, Element) else Text(i) for i in message])

        if isinstance(reply, Message):
            reply = reply.to_selector()
        elif isinstance(reply, str):
            reply = self.message(reply)

        return self.context[MessageSend.send](self, message, reply=reply)

    def remove_member(self, target: Selector, reason: str | None = None):
        return self.context[SceneCapability.remove_member](target, reason)


class ContextRequestSelector(ContextEndpointSelector):
    def accept_request(self):
        return self.context[RequestCapability.accept](self)

    def reject_request(self, reason: str | None = None, forever: bool = False):
        return self.context[RequestCapability.reject](self, reason, forever)

    def cancel_request(self):
        return self.context[RequestCapability.cancel](self)

    def ignore_request(self):
        return self.context[RequestCapability.ignore](self)


@dataclass
class ContextMedium:
    selector: ContextSelector
