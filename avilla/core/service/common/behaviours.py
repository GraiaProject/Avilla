from dataclasses import dataclass
from typing import Any, Callable

from avilla.core.service import ExportInterface
from avilla.core.service.entity import BehaviourDescription
from avilla.core.service.session import BehaviourSession
from avilla.core.stream import Stream


@dataclass
class PostConnected(BehaviourDescription[Callable[[ExportInterface, BehaviourSession, dict], Any]]):
    pass


@dataclass
class DataReceived(
    BehaviourDescription[Callable[[ExportInterface, BehaviourSession, dict, Stream[bytes]], Any]]
):
    pass


@dataclass
class PostDisconnected(BehaviourDescription[Callable[[ExportInterface, BehaviourSession, dict], Any]]):
    pass


@dataclass
class PreConnected(BehaviourDescription[Callable[[ExportInterface, BehaviourSession, dict], Any]]):
    pass
