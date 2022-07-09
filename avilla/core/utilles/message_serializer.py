from __future__ import annotations

import inspect
from typing import Any, Callable, ClassVar, Coroutine

from graia.amnesia.message import MessageChain
from graia.amnesia.message.element import Element
from graia.broadcast.utilles import run_always_await
from typing_extensions import Self


def element(element_type: type[Element]):
    def wrapper(func: Callable[[dict], Any]):
        func.__element_deserializer__ = element_type
        return func

    return wrapper


class MessageSerializer:
    element_serializer: ClassVar[dict[type[Element], Callable[[Self, Any], dict | Coroutine[None, None, dict]]]] = {}

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

    async def serialize_element(self, element: Element) -> dict:
        if type(element) not in self.element_serializer:
            raise NotImplementedError(f"Element type {type(element)} is not supported.")
        return await run_always_await(self.element_serializer[type(element)], self, element)  # type: ignore

    async def serialize_chain(self, message: MessageChain):
        return [await self.serialize_element(element) for element in message.content]
