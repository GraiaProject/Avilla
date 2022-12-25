from __future__ import annotations

from collections.abc import Awaitable, Iterable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypeVar

from graia.amnesia.message import Element, Text, __message_chain_class__
from typing_extensions import Self, TypeAlias, Unpack

from avilla.core.message import Message
from avilla.core.metadata import Metadata, MetadataOf, MetadataRoute
from avilla.core.selector import EMPTY_MAP, Selector
from avilla.core.trait import Trait
from avilla.spec.core.message import MessageSend
from avilla.spec.core.request import RequestTrait
from avilla.spec.core.scene import SceneTrait

if TYPE_CHECKING:
    from . import Context

_MetadataT = TypeVar("_MetadataT", bound=Metadata)
_DescribeT = TypeVar("_DescribeT", bound="type[Metadata] | MetadataRoute")
_TraitT = TypeVar("_TraitT", bound=Trait)

_Describe: TypeAlias = type[_MetadataT] | MetadataRoute[Unpack[tuple[Unpack[tuple[Any, ...]], _MetadataT]]]


class ContextSelector(Selector):
    context: Context

    def __init__(self, ctx: Context, pattern: Mapping[str, str] = EMPTY_MAP) -> None:
        super().__init__(pattern)
        self.context = ctx

    @classmethod
    def from_selector(cls, ctx: Context, selector: Selector) -> Self:
        return cls(ctx, selector.pattern)

    def pull(self, metadata: _Describe[_MetadataT]) -> Awaitable[_MetadataT]:
        return self.context.pull(metadata, self)

    def wrap(self, trait: type[_TraitT]) -> _TraitT:
        return trait(self.context, self)


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
        message: __message_chain_class__ | str | Iterable[str | Element],
        *,
        reply: Message | Selector | str | None = None,
    ):
        if isinstance(message, str):
            message = __message_chain_class__([Text(message)])
        elif not isinstance(message, __message_chain_class__):
            message = __message_chain_class__([]).extend(list(message))
        else:
            message = __message_chain_class__([i if isinstance(i, Element) else Text(i) for i in message])

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


@dataclass
class ContextWrappedMetadataOf(MetadataOf[_DescribeT]):
    context: Context

    def pull(self) -> Awaitable[_DescribeT]:
        return self.context.pull(self.describe, self.target)

    def wrap(self, trait: type[_TraitT]) -> _TraitT:
        return trait(self.context, self)
