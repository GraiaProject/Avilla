from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar

from graia.amnesia.message import MessageChain

from avilla.core import specialist
from avilla.core.platform import Base, Platform
from avilla.core.selectors import entity as entity_selector
from avilla.core.selectors import request as request_selector
from avilla.core.utilles.selector import Selector

from .execution import Execution

if TYPE_CHECKING:
    from avilla.core.relationship import Relationship

    from . import Avilla


class BaseProtocol(metaclass=ABCMeta):
    platform_base: ClassVar[Base] = specialist.avilla_platform_base
    platform: ClassVar[Platform] = Platform(platform_base)

    @abstractmethod
    async def ensure_execution(self, execution: "Execution") -> Any:
        raise NotImplementedError

    @abstractmethod
    async def parse_message(self, data: Any) -> "MessageChain":
        raise NotImplementedError

    @abstractmethod
    async def serialize_message(self, message: "MessageChain") -> Any:
        raise NotImplementedError

    @abstractmethod
    async def get_relationship(self, ctx: Selector, current_self: entity_selector) -> "Relationship":
        raise NotImplementedError

    @abstractmethod
    def ensure(self, avilla: Avilla) -> Any:
        ...

    def complete_selector(self, selector: Selector) -> Selector:
        return selector

    async def accept_request(self, request: request_selector):
        raise NotImplementedError

    async def reject_request(self, request: request_selector):
        raise NotImplementedError

    async def ignore_request(self, request: request_selector):
        raise NotImplementedError
