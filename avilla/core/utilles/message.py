from abc import ABCMeta, abstractmethod
from typing import Any, Awaitable, Callable, Dict, Generic, List, Type, TypeVar, Union

from avilla.core.message import Element, MessageChain

T = TypeVar("T", bound=Element)
P = TypeVar("P")


class MessageSerializer(Generic[P]):
    serializers: Dict[Type[Element], Callable[[P, Element], Awaitable[Any]]] = {}

    def __init_subclass__(cls, **kwargs):
        cls.serializers = {}
        for base in reversed(cls.__bases__):
            if issubclass(base, MessageSerializer):
                cls.serializers.update(base.serializers)

    async def serialize(self, protocol: P, message: MessageChain) -> List[Any]:
        result = []

        for element in message.content:
            message_type = element.__class__
            if message_type in self.serializers:
                result.append(await self.serializers[message_type](protocol, element))
            else:
                raise ValueError(f"[{message_type}] cannot be serialized.")

        return result


class AbstractMessageParser(Generic[P], metaclass=ABCMeta):
    parsers: Dict[Type[Element], Callable[[P, Element], Awaitable[Any]]] = {}

    @abstractmethod
    def type_getter(self, token: Any) -> Type[Element]:
        raise NotImplementedError

    def __init_subclass__(cls, **kwargs):
        cls.parsers = {}
        for base in reversed(cls.__bases__):
            if issubclass(base, AbstractMessageParser):
                cls.parsers.update(base.parsers)

    async def parse(self, protocol: P, message: List[Any]) -> MessageChain:
        result = []

        for element in message:
            message_type = self.type_getter(element)
            if message_type in self.parsers:
                result.append(await self.parsers[message_type](protocol, element))
            else:
                raise ValueError(f"[{message_type}] cannot be parsed.")

        return MessageChain(result)
