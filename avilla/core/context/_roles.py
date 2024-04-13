from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeVar

from graia.amnesia.message import Element, MessageChain, Text
from typing_extensions import ParamSpec

from avilla.core.builtins.capability import CoreCapability
from avilla.core.message import Message
from avilla.core.metadata import Metadata
from avilla.core.selector import Selector
from avilla.standard.core.activity import ActivityTrigger
from avilla.standard.core.message import MessageSend
from avilla.standard.core.relation import SceneCapability
from avilla.standard.core.request import RequestCapability

from ._selector import ContextSelector

if TYPE_CHECKING:
    pass

R = TypeVar("R", covariant=True)
P = ParamSpec("P")
_MetadataT = TypeVar("_MetadataT", bound=Metadata)


class ContextClientSelector(ContextSelector):
    def trigger_activity(self, activity: str):
        return self.context[ActivityTrigger.trigger](self.activity(activity))

    @property
    def channel(self) -> str:
        return self.context.staff.call_fn(CoreCapability.channel, self)

    @property
    def guild(self) -> str | None:
        try:
            return self.context.staff.call_fn(CoreCapability.guild, self)
        except NotImplementedError:
            return None

    @property
    def user(self) -> str:
        return self.context.staff.call_fn(CoreCapability.user, self)


class ContextEndpointSelector(ContextSelector):
    def expects_request(self) -> ContextRequestSelector:
        if "request" in self.pattern:
            return ContextRequestSelector.from_selector(self.context, self)

        raise ValueError(f"endpoint {self!r} is not a request endpoint")

    @property
    def channel(self) -> str:
        return self.context.staff.call_fn(CoreCapability.channel, self)

    @property
    def guild(self) -> str | None:
        try:
            return self.context.staff.call_fn(CoreCapability.guild, self)
        except NotImplementedError:
            return None

    @property
    def user(self) -> str:
        return self.context.staff.call_fn(CoreCapability.user, self)


class ContextSelfSelector(ContextSelector):
    def trigger_activity(self, activity: str):
        return self.context[ActivityTrigger.trigger](self.activity(activity))


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

    def remove_member(self, target: Selector, reason: str | None = None, permanent: bool = False):
        return self.context[SceneCapability.remove_member](target, reason, permanent)

    @property
    def channel(self) -> str:
        return self.context.staff.call_fn(CoreCapability.channel, self)

    @property
    def guild(self) -> str:
        return self.context.staff.call_fn(CoreCapability.guild, self)


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
