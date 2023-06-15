from __future__ import annotations

from collections.abc import Awaitable, Iterable, Mapping
from typing import TYPE_CHECKING, Protocol, TypeVar

from graia.amnesia.message import Element, MessageChain, Text
from typing_extensions import Self

from avilla.core._vendor.dataclasses import dataclass
from avilla.core.message import Message
from avilla.core.metadata import Metadata, MetadataRoute
from avilla.core.selector import EMPTY_MAP, Selector

if TYPE_CHECKING:
    from . import Context, _Describe

_MetadataT = TypeVar("_MetadataT", bound=Metadata)
_DescribeT = TypeVar("_DescribeT", bound="type[Metadata] | MetadataRoute")

_R = TypeVar("_R", covariant=True)



class ContextSelector(Selector):
    context: Context

    def __init__(self, cx: Context, pattern: Mapping[str, str] = EMPTY_MAP) -> None:
        super().__init__(pattern)
        self.context = cx

    @classmethod
    def from_selector(cls, cx: Context, selector: Selector) -> Self:
        return cls(cx, selector.pattern)

    def pull(self, metadata: _Describe[_MetadataT]) -> Awaitable[_MetadataT]:
        return self.context.pull(metadata, self)


class ContextClientSelector(ContextSelector):
    ...


class ContextEndpointSelector(ContextSelector):
    def expects_request(self) -> ContextRequestSelector:
        if "request" in self.pattern:
            return ContextRequestSelector.from_selector(self.context, self)

        raise ValueError(f"endpoint {self!r} is not a request endpoint")


class ContextSceneSelector(ContextSelector):
    def leave_scene(self):
        return self.wrap(SceneTrait).leave()

    def disband_scene(self):
        return self.wrap(SceneTrait).disband()

    def send_message(
        self,
        message: MessageChain | str | Iterable[str | Element],
        *,
        reply: Message | Selector | str | None = None,
    ):
        if isinstance(message, str):
            message = MessageChain([Text(message)])
        elif not isinstance(message, MessageChain):
            message = MessageChain([]).extend(list(message))
        else:
            message = MessageChain([i if isinstance(i, Element) else Text(i) for i in message])

        if isinstance(reply, Message):
            reply = reply.to_selector()
        elif isinstance(reply, str):
            reply = self.message(reply)

        return self.wrap(MessageSend).send(message, reply=reply)

    def remove_member(self, target: Selector, reason: str | None = None):
        return self.wrap(SceneTrait).remove_member(reason)


class ContextRequestSelector(ContextEndpointSelector):
    def accept_request(self):
        return self.wrap(RequestTrait).accept()

    def reject_request(self, reason: str | None = None, forever: bool = False):
        return self.wrap(RequestTrait).reject(reason, forever)

    def cancel_request(self):
        return self.wrap(RequestTrait).cancel()

    def ignore_request(self):
        return self.wrap(RequestTrait).ignore()


@dataclass
class ContextMedium:
    selector: ContextSelector
