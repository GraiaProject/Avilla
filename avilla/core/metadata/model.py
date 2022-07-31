from __future__ import annotations

import inspect
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, TypeVar, overload

from typing_extensions import TypeVarTuple, Unpack

if TYPE_CHECKING:
    from avilla.core.metadata.source import MetadataSource
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


_Meta_A = TypeVar("_Meta_A", bound="MetadataMCS")

_Meta_B = TypeVar("_Meta_B", bound="MetadataMCS")


TVT = TypeVarTuple("TVT")


class MetadataMCS(ABCMeta):
    @overload
    def __rshift__(cls: _Meta_A, other: _Meta_B) -> CellCompose[_Meta_A, _Meta_B]:
        ...

    @overload
    def __rshift__(cls: _Meta_A, other: CellCompose[Unpack[TVT]]) -> CellCompose[_Meta_A, Unpack[TVT]]:
        ...

    def __rshift__(cls, other: MetadataMCS | CellCompose) -> CellCompose:
        cells = (cls, other) if isinstance(other, MetadataMCS) else (cls, *other.cells)
        return CellCompose(cells)


class Metadata(Generic[T], metaclass=MetadataMCS):
    _target: Any
    _source: MetadataSource
    _content: dict[str, Any]
    _modifies: MetadataModifies[T] | None = None

    def __init__(self, *, target: Any, source: MetadataSource, content: dict[str, Any] | None = None) -> None:
        self._target = target
        self._source = source
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
    def get_default_target(cls, relationship: Relationship) -> Selector | None:
        return relationship.ctx


Ts = TypeVarTuple("Ts")


class CellCompose(Generic[Unpack[TVT]]):
    cells: tuple[Unpack[TVT]]

    def __init__(self, cells: tuple[Unpack[TVT]]) -> None:
        self.cells = cells

    @overload
    def __rshift__(self: CellCompose[Unpack[TVT]], other: _Meta_A) -> CellCompose[Unpack[TVT], _Meta_A]:
        ...

    @overload
    def __rshift__(
        self: CellCompose[Unpack[TVT]], other: CellCompose[Unpack[Ts]]
    ) -> CellCompose[Unpack[TVT], Unpack[Ts]]:
        ...

    def __rshift__(self, other: MetadataMCS | CellCompose) -> CellCompose:
        cells = (*self.cells, other) if isinstance(other, MetadataMCS) else (*self.cells, *other.cells)
        return CellCompose(cells)
