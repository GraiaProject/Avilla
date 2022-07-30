from __future__ import annotations
import inspect
from typing import TYPE_CHECKING, AsyncGenerator, AsyncIterator, Callable, ClassVar, Generic, TypeVar
from typing_extensions import Self

from avilla.core.utilles.selector import Selector

if TYPE_CHECKING:
    from avilla.core.relationship import Relationship
    from avilla.core.protocol import BaseProtocol


def query(target: str):
    def wrapper(func):
        func.__query_key__ = target
        return func
    return wrapper

class AbstractQueryHandler:
    prefix: Selector
    queriers: ClassVar[dict[str, Callable[[Self, Relationship, Selector, Callable[[Selector], bool]], AsyncGenerator[Selector, None]]]] = {}

    def __init_subclass__(cls, prefix: Selector | None = None):
        super().__init_subclass__()
        cls.queriers = {}
        cls.prefix = prefix or Selector.any()
        for mro in reversed(inspect.getmro(cls)):
            if issubclass(mro, AbstractQueryHandler):
                cls.queriers.update(mro.queriers)
        members = inspect.getmembers(cls, predicate=inspect.isfunction)
        for _, value in members:
            if hasattr(value, "__query_key__"):
                cls.queriers[value.__query_key__] = value

TProtocol = TypeVar("TProtocol", bound="BaseProtocol")

class ProtocolAbstractQueryHandler(AbstractQueryHandler, Generic[TProtocol]):
    protocol: TProtocol

    def __init__(self, protocol: TProtocol) -> None:
        self.protocol = protocol

    def __init_subclass__(cls, prefix: Selector):
        super().__init_subclass__(prefix)