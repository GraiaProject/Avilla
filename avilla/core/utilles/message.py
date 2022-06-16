from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from graia.amnesia.message import Element, MessageChain

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


T = TypeVar("T", bound=Element)
P = TypeVar("P")


class MessageSerializer(Generic[P]):
    serializers: dict[type[Element], Callable[[P, Element], Awaitable[Any]]] = {}

    def __init_subclass__(cls, **kwargs):
        cls.serializers = {}
        for base in reversed(cls.__bases__):
            if issubclass(base, MessageSerializer):
                cls.serializers.update(base.serializers)

    async def serialize(self, protocol: P, message: MessageChain) -> list[Any]:
        result = []

        for element in message.content:
            message_type = element.__class__
            if message_type in self.serializers:
                result.append(await self.serializers[message_type](protocol, element))
            else:
                raise ValueError(f"[{message_type}] cannot be serialized.")

        return result


class AbstractMessageParser(Generic[P], metaclass=ABCMeta):
    parsers: dict[type[Element], Callable[[P, Element], Awaitable[Any]]] = {}

    @abstractmethod
    def type_getter(self, token: Any) -> type[Element]:
        raise NotImplementedError

    def __init_subclass__(cls, **kwargs):
        cls.parsers = {}
        for base in reversed(cls.__bases__):
            if issubclass(base, AbstractMessageParser):
                cls.parsers.update(base.parsers)

    async def parse(self, protocol: P, message: list[Any]) -> MessageChain:
        result = []

        for element in message:
            message_type = self.type_getter(element)
            if message_type in self.parsers:
                result.append(await self.parsers[message_type](protocol, element))
            else:
                raise ValueError(f"[{message_type}] cannot be parsed.")

        return MessageChain(result)
