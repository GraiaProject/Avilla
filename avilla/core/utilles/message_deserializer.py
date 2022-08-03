from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Coroutine,
    Generic,
    Iterable,
    TypeVar,
)

from graia.amnesia.message.element import Element
from graia.broadcast.utilles import run_always_await
from typing_extensions import Self

from avilla.core.elements import Unknown

if TYPE_CHECKING:
    from avilla.core.protocol import BaseProtocol


def deserializer(element_type: str):
    def wrapper(func):
        func.__element_deserializer__ = element_type
        return func

    return wrapper


_P = TypeVar("_P", bound="BaseProtocol")


class MessageDeserializer(ABC, Generic[_P]):
    element_deserializer: dict[str, Callable[[Self, _P, dict], Element | Coroutine[None, None, Element]]] = {}
    ignored_types: set[str] = set()

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.element_deserializer = {}
        for mro in reversed(inspect.getmro(cls)):
            if issubclass(mro, MessageDeserializer):
                cls.element_deserializer.update(mro.element_deserializer)
        members = inspect.getmembers(cls)
        for _, value in members:
            if callable(value) and getattr(value, "__element_deserializer__", False):
                cls.element_deserializer[value.__element_deserializer__] = value

    def split_message(self, data: list) -> Iterable[dict]:
        yield from data

    @abstractmethod
    def get_element_type(self, raw: dict) -> str:
        ...

    async def parse_element(self, protocol: _P, raw: dict) -> Element:
        element_type = self.get_element_type(raw)
        deserializer = self.element_deserializer.get(element_type)
        if deserializer is None:
            return Unknown(type=element_type, raw_data=raw)
        return await run_always_await(deserializer, self, protocol, raw)  # type: ignore

    async def parse_sentence(self, protocol: _P, data: list) -> list[Any]:
        return [
            await self.parse_element(protocol, raw)
            for raw in self.split_message(data)
            if self.get_element_type(raw) not in self.ignored_types
        ]
