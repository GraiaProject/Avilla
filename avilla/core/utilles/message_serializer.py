from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Coroutine, Generic, TypeVar

from graia.amnesia.message import MessageChain
from graia.amnesia.message.element import Element
from graia.broadcast.utilles import run_always_await
from typing_extensions import Self

if TYPE_CHECKING:
    from avilla.core.protocol import BaseProtocol


def element(element_type: type[Element]):
    def wrapper(func: Callable):
        func.__element_serializer__ = element_type
        return func

    return wrapper


_P = TypeVar("_P", bound="BaseProtocol")


class MessageSerializer(Generic[_P]):
    element_serializer: dict[type[Element], Callable[[Self, _P, Any], dict | Coroutine[None, None, dict]]] = {}

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.element_serializer = {}
        for mro in reversed(inspect.getmro(cls)):
            if issubclass(mro, MessageSerializer):
                cls.element_serializer.update(mro.element_serializer)
        members = inspect.getmembers(cls)
        for _, value in members:
            if callable(value) and getattr(value, "__element_serializer__", False):
                cls.element_serializer[value.__element_serializer__] = value

    async def serialize_element(self, protocol: _P, element: Element) -> dict:
        if type(element) not in self.element_serializer:
            raise NotImplementedError(f"Element type {type(element)} is not supported.")
        return await run_always_await(self.element_serializer[type(element)], self, protocol, element)  # type: ignore

    async def serialize_chain(self, protocol: _P, message: MessageChain):
        return [await self.serialize_element(protocol, element) for element in message.content]
