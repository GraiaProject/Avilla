from __future__ import annotations

import inspect
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
)

if TYPE_CHECKING:
    from avilla.core.relationship import Relationship
    from avilla.core.utilles.selector import Selector

T = TypeVar("T")  # 返回值


@dataclass
class MetadataModifies(Generic[T]):
    target: Any
    model: Type["Metadata"]
    modified: List[str]
    past: Dict[str, Any]
    current: Dict[str, Any]


M = TypeVar("M", bound=MetadataModifies)


class MetaField:
    id: str

    def __init__(self, id: str) -> None:
        self.id = id

    def __get__(self, instance: Metadata | None, owner) -> Any:
        # sourcery skip: assign-if-exp, reintroduce-else
        if instance is None:
            return self
        return instance._content[self.id]

    def __set__(self, instance: Metadata, value: Any) -> None:
        if instance._modifies is None:
            instance._modifies = MetadataModifies(instance, instance.__class__, [], {}, {})
        instance._modifies.modified.append(self.id)
        instance._modifies.past[self.id] = instance._content[self.id]
        instance._modifies.current[self.id] = value
        instance._content[self.id] = value


def meta_field(id: str) -> Any:
    return MetaField(id)


class Metadata(Generic[T], metaclass=ABCMeta):
    _content: Dict[str, Any]
    _modifies: Optional[MetadataModifies] = None

    def __init__(self, *, content: Optional[Dict[str, Any]] = None) -> None:
        self._content = content or {}

    @abstractmethod
    def modifies(self) -> Optional[MetadataModifies[T]]:
        return self._modifies

    @classmethod
    def fields(cls) -> List[MetaField]:
        return [v for _, v in inspect.getmembers(cls, lambda x: isinstance(x, MetaField))]

    def __repr__(self) -> str:
        values = ", ".join(f"{k}={repr(v)}" for k, v in self._content.items() if not k.startswith("_"))
        return f"{self.__class__.__name__}({values})"

    @classmethod
    def default_target_by_relationship(cls, relationship: "Relationship") -> Selector | None:
        pass
