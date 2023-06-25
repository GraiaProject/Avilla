from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Union

TJsonLiteralValue = Union[str, int, float, bool, None]
TJsonKey = Union[str, int]
TJsonStructure = Union["dict[TJsonKey, TJson]", "list[TJson]", "tuple[TJson, ...]"]
TJson = Union[TJsonLiteralValue, TJsonStructure]

TJsonCustomSerializer = Callable[[Any], TJson]

# 因为 tuple 虽然是 Hashable & builtin & Immutable, 但是不符合 JSON 规范, 所以 tuple 无法作为 TJsonKey.
# bytes 不必说.


class JSONBackend(metaclass=ABCMeta):
    @abstractmethod
    def serialize(self, value: TJson, *, custom_serializers: dict[type, TJsonCustomSerializer] | None = None) -> str:
        raise NotImplementedError()

    @abstractmethod
    def deserialize(self, value: str) -> TJson:
        raise NotImplementedError()

    def serialize_as_bytes(
        self, value: Any, *, custom_serializers: dict[type, TJsonCustomSerializer] | None = None
    ) -> bytes:
        return self.serialize(value, custom_serializers=custom_serializers).encode("utf-8")


from .bootstrap import CURRENT_BACKEND as CURRENT_BACKEND
from .frontend import Json as Json
