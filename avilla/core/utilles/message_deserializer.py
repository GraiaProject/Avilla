from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from typing import Any, Callable, ClassVar, Coroutine, Iterable

from graia.amnesia.message.element import Element
from graia.broadcast.utilles import run_always_await
from typing_extensions import Self


def deserializer(func: Callable[[dict], Any]):
    func.__element_deserializer__ = True
    return func


class MessageDeserializer(ABC):
    element_deserializer: ClassVar[dict[str, Callable[[Self, dict], Element | Coroutine[None, None, Element]]]] = {}

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.element_deserializer = {}
        for mro in reversed(inspect.getmro(cls)):
            if issubclass(mro, MessageDeserializer):
                cls.element_deserializer.update(mro.element_deserializer)
        members = inspect.getmembers(cls)
        for _, value in members:
            if callable(value) and getattr(value, "__element_deserializer__", False):
                cls.element_deserializer[value.__name__] = value

    def split_message(self, data: list) -> Iterable[dict]:
        yield from data

    @abstractmethod
    def get_element_type(self, raw: dict) -> str:
        ...

    async def parse_element(self, raw: dict) -> Element:
        element_type = self.get_element_type(raw)
        deserializer = self.element_deserializer.get(element_type)
        if deserializer is None:
            raise NotImplementedError(f"Element type {element_type} is not supported.")
        return await run_always_await(deserializer, self, raw)  # type: ignore

    async def parse_sentence(self, data: list) -> list[Any]:
        return [await self.parse_element(raw) for raw in self.split_message(data)]
