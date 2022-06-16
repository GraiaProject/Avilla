from __future__ import annotations

import inspect
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from avilla.core.relationship import Relationship
    from avilla.core.utilles.selector import Selector

T = TypeVar("T")  # 返回值


@dataclass
class MetadataModifies(Generic[T]):
    target: Any
    model: type[Metadata]
    modified: list[str]
    past: dict[str, Any]
    current: dict[str, Any]


M = TypeVar("M", bound=MetadataModifies)


class MetaField:
    id: str

    def __init__(self, id: str) -> None:
        self.id = id

    def __get__(self, instance: Metadata | None, owner: type[Metadata]) -> Any:
        # sourcery skip: assign-if-exp, reintroduce-else
        if instance is None:
            return self
        return instance._content[self.id]

    def __set__(self, instance: Metadata, value: Any) -> None:
        modifies = instance._modifies
        if modifies is None:
            modifies = MetadataModifies(instance, instance.__class__, [], {}, {})
        modifies.modified.append(self.id)
        modifies.past[self.id] = instance._content[self.id]
        modifies.current[self.id] = value
        instance._content[self.id] = value


def meta_field(id: str) -> Any:
    return MetaField(id)


class Metadata(Generic[T], metaclass=ABCMeta):
    _content: dict[str, Any]
    _modifies: MetadataModifies[T] | None = None

    def __init__(self, *, content: dict[str, Any] | None = None) -> None:
        self._content = content or {}

    @abstractmethod
    def modifies(self) -> MetadataModifies[T] | None:
        return self._modifies

    @classmethod
    def fields(cls) -> list[MetaField]:
        return [v for _, v in inspect.getmembers(cls, lambda x: isinstance(x, MetaField))]

    def __repr__(self) -> str:
        values = ", ".join(f"{k}={repr(v)}" for k, v in self._content.items() if not k.startswith("_"))
        return f"{self.__class__.__name__}({values})"

    @classmethod
    def default_target_by_relationship(cls, relationship: Relationship[Selector]) -> Selector | None:
        return relationship.ctx
