from abc import ABCMeta
from typing import Any, Callable, Coroutine, Dict, Generic, List, Tuple, Type, TypeVar
from typing_extensions import TypeVarTuple, Unpack

from avilla.core.metadata import Metadata
from avilla.core.relationship import Relationship

M = TypeVar("M", bound=Metadata)
TTV = TypeVarTuple("TTV")

# 似乎出了点问题: 这个好像很麻烦, 没法给 Resource 用
class MetadataFieldAllocator(metaclass=ABCMeta):
    handlers: Dict[Tuple[str], Callable[[Relationship, Tuple[str]], Coroutine[None, None, Dict[str, Any]]]]

    def __init_subclass__(cls, **kwargs):
        cls.handlers = {}
        for base in reversed(cls.__bases__):
            if issubclass(base, MetadataFieldAllocator):
                cls.handlers.update(base.handlers)

    async def allocate(self, metaclass: Type[M], relationship: Relationship) -> M:
        gathered_values = {}
        fields = metaclass.fields()
        field_ids = {i.id for i in fields}
        for allocated_fields, handler in self.handlers.items():
            occasion = tuple(field_ids.intersection(allocated_fields))
            if occasion:
                gathered_values.update(await handler(relationship, occasion))
        return metaclass.from_fields(gathered_values)
