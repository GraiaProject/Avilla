from dataclasses import dataclass
from typing import TYPE_CHECKING, Awaitable, Callable

from graia.amnesia.message.element import Element
from typing_extensions import TypeAlias

from avilla.core.context import Context
from avilla.core.event import AvillaEvent

from ...core.trait.context import get_artifacts
from ...core.trait.signature import ArtifactSignature

if TYPE_CHECKING:
    from ..account import ElizabethAccount
    from ..protocol import ElizabethProtocol


@dataclass(unsafe_hash=True)
class EventParse(ArtifactSignature):
    event_type: str


EventParser: TypeAlias = Callable[
    ["ElizabethProtocol", "ElizabethAccount", dict], Awaitable[tuple[AvillaEvent, Context]]
]


def event(event_type: str):
    def wrapper(handler: EventParser):
        artifacts = get_artifacts()
        artifacts[EventParse(event_type)] = handler
        return handler

    return wrapper


@dataclass(unsafe_hash=True)
class ElementParse(ArtifactSignature):
    element_type: str


ElementParser: TypeAlias = Callable[[Context, dict], Awaitable[Element]]


def element(element_type: str):
    def wrapper(handler: ElementParser):
        artifacts = get_artifacts()
        artifacts[ElementParse(element_type)] = handler
        return handler

    return wrapper
