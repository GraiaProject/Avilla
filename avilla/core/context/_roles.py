from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeVar

from typing_extensions import ParamSpec

from avilla.core.builtins.capability import CoreCapability
from avilla.core.message import Message
from avilla.core.metadata import Metadata
from avilla.core.selector import Selector
from avilla.standard.core.activity import start_activity
from avilla.standard.core.message import send_message
from avilla.standard.core.relation import leave_scene, disband_scene, remove_member
from avilla.standard.core.request import accept_request, reject_request, cancel_request, ignore_request
from graia.amnesia.message import Element, MessageChain, Text

from ._selector import ContextSelector

if TYPE_CHECKING:
    pass

R = TypeVar("R", covariant=True)
P = ParamSpec("P")
_MetadataT = TypeVar("_MetadataT", bound=Metadata)


class ContextClientSelector(ContextSelector):
    def trigger_activity(self, activity: str):
        return start_activity(self.activity(activity))

    @property
    def channel(self) -> str:
        return CoreCapability.channel(self)

    @property
    def guild(self) -> str | None:
        try:
            return CoreCapability.guild(self)
        except NotImplementedError:
            return None

    @property
    def user(self) -> str:
        return CoreCapability.user(self)


class ContextEndpointSelector(ContextSelector):
    def expects_request(self) -> ContextRequestSelector:
        if "request" in self.pattern:
            return ContextRequestSelector.from_selector(self.context, self)

        raise ValueError(f"endpoint {self!r} is not a request endpoint")

    @property
    def channel(self) -> str:
        return CoreCapability.channel(self)

    @property
    def guild(self) -> str | None:
        try:
            return CoreCapability.guild(self)
        except NotImplementedError:
            return None

    @property
    def user(self) -> str:
        return CoreCapability.user(self)


class ContextSelfSelector(ContextSelector):
    def trigger_activity(self, activity: str):
        return start_activity(self.activity(activity))


class ContextSceneSelector(ContextSelector):
    def leave_scene(self):
        return leave_scene(self)

    def disband_scene(self):
        return disband_scene(self)

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

        return send_message(self, message, reply=reply)

    def remove_member(self, target: Selector, reason: str | None = None):
        return remove_member(target, reason)

    @property
    def channel(self) -> str:
        return CoreCapability.channel(self)

    @property
    def guild(self) -> str:
        return CoreCapability.guild(self)


class ContextRequestSelector(ContextEndpointSelector):
    def accept(self):
        return accept_request(self)

    def reject(self, reason: str | None = None, forever: bool = False):
        return reject_request(self, reason, forever)

    def cancel(self):
        return cancel_request(self)

    def ignore(self):
        return ignore_request(self)


@dataclass
class ContextMedium:
    selector: ContextSelector
