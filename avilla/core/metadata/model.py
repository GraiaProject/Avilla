from __future__ import annotations
from contextlib import suppress

import inspect
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, TypeVar, overload

from typing_extensions import Self

if TYPE_CHECKING:
    from avilla.core.metadata.source import MetadataSource
    from avilla.core.relationship import Relationship
    from avilla.core.utilles.selector import Selector

T = TypeVar("T")  # 返回值


@dataclass
class Modify:
    id: str
    method: str

    past: Any
    current: Any


# TODO: 更多的"更改"类型描述. 现在这种叫 set.


class MetaField(Generic[T]):
    id: str
    optional: bool
    lazy: bool

    def __init__(self, id: str, *, optional: bool = False, lazy: bool = False) -> None:
        self.id = id
        if optional and lazy:
            raise ValueError("field cannot be both optional and lazy")
        self.optional = optional
        self.lazy = lazy

    @overload
    def __get__(self, instance: None, owner: None) -> MetaField:
        ...

    @overload
    def __get__(self, instance: Metadata, owner: type[MetaField]) -> T:
        ...

    def __get__(
        self, instance: Metadata | None, owner: type[MetaField] | None = None
    ) -> T | MetaField:
        # sourcery skip: assign-if-exp, reintroduce-else
        if instance is None:
            return self
        return instance._content[self.id]

    def __set__(self, instance: Metadata, value: Any) -> None:
        modifies = instance._modifies
        if modifies is None:
            modifies = []
        modifies.append(Modify(self.id, "set", instance._content[self.id], value))
        instance._content[self.id] = value


def meta_field(id: str) -> Any:
    return MetaField(id)


TMetadata = TypeVar("TMetadata", bound="Metadata")

class Component(Generic[TMetadata]):
    model: type[TMetadata]
    optional: bool
    lazy: bool

    def __init__(self, model: type[TMetadata], *, optional: bool = False, lazy: bool = False) -> None:
        self.model = model
        if optional and lazy:
            raise ValueError("field cannot be both optional and lazy")
        self.optional = optional
        self.lazy = lazy
    
    @overload
    def __get__(self, instance: None, owner: None) -> Self:
        ...

    @overload
    def __get__(self, instance: Metadata, owner: type[MetaField]) -> TMetadata:
        ...

    def __get__(
        self, instance: Metadata | None, owner: type[MetaField] | None = None
    ) -> TMetadata | Self:
        if instance is None:
            return self
        if any(i.id not in instance._content for i in self.model.fields() if not i.optional):
            if self.lazy:
                # TODO: lazy 的形式
                raise RuntimeError("lazy component must be initialized before use, use `rs.meta.ensure()` or `rs.meta(..., ensure=True)`")
            raise RuntimeError(f"Missing required fields for {self.model.__name__}")
        return self.model(instance._source, content=instance._content)

class Metadata(Generic[T], metaclass=ABCMeta):
    _content: dict[str, Any]
    _modifies: list[Modify] | None = None
    _source: MetadataSource

    def __init__(self, _source: MetadataSource, *, content: dict[str, Any] | None = None) -> None:
        self._source = _source
        self._content = content or {}

    @abstractmethod
    def modifies(self) -> list[Modify] | None:
        return self._modifies

    @classmethod
    def fields(cls) -> list[MetaField]:
        return [v for _, v in inspect.getmembers(cls, lambda x: isinstance(x, MetaField))]
    
    @classmethod
    def fields_required(cls) -> list[MetaField]:
        return [v for v in cls.fields() if not v.optional]

    def __repr__(self) -> str:
        values = ", ".join(f"{k}={repr(v)}" for k, v in self._content.items() if not k.startswith("_"))
        return f"{self.__class__.__name__}({values})"

    @classmethod
    def get_default_target(cls, relationship: Relationship) -> Selector | None:
        return relationship.ctx
