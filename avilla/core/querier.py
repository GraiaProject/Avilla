from __future__ import annotations

import inspect
from collections.abc import AsyncGenerator, Callable
from typing import TYPE_CHECKING, ClassVar, Generic, TypeVar

from typing_extensions import Self

from avilla.core.selector import Selector

if TYPE_CHECKING:
    from avilla.core.context import Context
    from avilla.core.protocol import BaseProtocol


def query(target: str):
    def wrapper(func):
        func.__query_key__ = target
        return func

    return wrapper


class AbstractQueryHandler:
    prefix: str | None
    queriers: ClassVar[
        dict[
            str,
            Callable[[Self, Context, Selector, Callable[[Selector], bool]], AsyncGenerator[Selector, None]],
        ]
    ] = {}

    def __init_subclass__(cls, prefix: str | None = None):
        super().__init_subclass__()
        cls.queriers = {}
        cls.prefix = prefix
        for mro in reversed(inspect.getmro(cls)):
            if issubclass(mro, AbstractQueryHandler):
                cls.queriers |= mro.queriers
        members = inspect.getmembers(cls, predicate=inspect.isfunction)
        for _, value in members:
            if query_key := getattr(value, "__query_key__", None):
                cls.queriers[query_key] = value


TProtocol = TypeVar("TProtocol", bound="BaseProtocol")


class ProtocolAbstractQueryHandler(AbstractQueryHandler, Generic[TProtocol]):
    protocol: TProtocol

    def __init__(self, protocol: TProtocol) -> None:
        self.protocol = protocol
